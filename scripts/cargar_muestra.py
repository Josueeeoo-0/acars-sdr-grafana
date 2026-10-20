#!/usr/bin/env python3
"""Valida y reproduce en Loki la muestra original de ACARS, sin SDR."""

import argparse
import json
import sys
import time
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SAMPLE = Path(__file__).resolve().parent.parent / "ejemplos" / "recepcion_acars.jsonl"
EXPECTED_MSGNOS = {"S12A", "S35A", "S36A", "M52A", "M50A", "M51A", "S66A", "S67A", "S69A"}
LABELS = {"job": "acarsdec-demo", "station": "Dragon26", "freq": "131.725"}
EXPECTED_FLIGHTS = {
    "CC-BFO": "LP2055",
    "CC-BFW": "LP2267",
    "CC-CPJ": "LP2205",
    "CC-BAH": "LP2067",
}
EXPECTED_TAIL_COUNTS = {"CC-BFO": 1, "CC-BFW": 2, "CC-CPJ": 1, "CC-BAH": 5}


def _number(value):
    return isinstance(value, (int, Decimal)) and not isinstance(value, bool)


def load_and_validate(path):
    if not path.is_file():
        raise ValueError(
            f"No se encontró la muestra original: {path}\n"
            "Copia recepcion_acars.jsonl desde la captura original a ejemplos/; "
            "este script no genera datos de ejemplo."
        )
    records = []
    lines = []
    try:
        with path.open("r", encoding="utf-8") as source:
            for line_no, raw in enumerate(source, 1):
                line = raw.rstrip("\r\n")
                if not line.strip():
                    raise ValueError(f"línea {line_no}: línea vacía; se esperaba un objeto JSON")
                try:
                    item = json.loads(
                        line,
                        parse_float=Decimal,
                        parse_int=Decimal,
                        parse_constant=lambda value: (_ for _ in ()).throw(
                            ValueError(f"constante no finita {value}")
                        ),
                    )
                except (json.JSONDecodeError, InvalidOperation, ValueError) as exc:
                    raise ValueError(f"línea {line_no}: JSON inválido ({exc})") from None
                if not isinstance(item, dict):
                    raise ValueError(f"línea {line_no}: se esperaba un objeto JSON")
                ts = item.get("timestamp")
                if not _number(ts) or not ts.is_finite():
                    raise ValueError(f"línea {line_no}: timestamp debe ser numérico y finito")
                freq = item.get("freq")
                if not _number(freq) or not freq.is_finite():
                    raise ValueError(f"línea {line_no}: freq debe ser numérica y finita")
                if freq != Decimal("131.725"):
                    raise ValueError(f"línea {line_no}: freq debe ser 131.725 MHz")
                if item.get("station_id") != "Dragon26":
                    raise ValueError(f"línea {line_no}: station_id debe ser Dragon26")
                for key in ("tail", "flight", "msgno", "text"):
                    if not isinstance(item.get(key), str):
                        raise ValueError(f"línea {line_no}: {key} debe ser texto")
                error = item.get("error")
                if not _number(error) or not error.is_finite():
                    raise ValueError(f"línea {line_no}: error debe ser numérico y finito")
                if error != 0:
                    raise ValueError(f"línea {line_no}: error debe ser 0")
                records.append(item)
                lines.append(line)
    except UnicodeError as exc:
        raise ValueError(f"La muestra no es UTF-8 válido: {exc}") from None
    except OSError as exc:
        raise ValueError(f"No se pudo leer la muestra: {exc}") from None

    if len(records) != 9:
        raise ValueError(f"La muestra debe contener 9 registros; contiene {len(records)}")
    tails = Counter(record["tail"] for record in records)
    if dict(tails) != EXPECTED_TAIL_COUNTS:
        raise ValueError("La distribución esperada es CC-BFO:1, CC-BFW:2, CC-CPJ:1 y CC-BAH:5")
    if any(EXPECTED_FLIGHTS.get(record["tail"]) != record["flight"] for record in records):
        raise ValueError("La relación matrícula/vuelo no coincide con la muestra original")
    msgnos = {record["msgno"] for record in records}
    if msgnos != EXPECTED_MSGNOS:
        raise ValueError("Los códigos msgno no coinciden con los nueve mensajes originales")
    text_count = sum(bool(record["text"]) for record in records)
    if text_count != 3:
        raise ValueError(f"La muestra debe tener 3 mensajes con text no vacío; contiene {text_count}")
    return records, lines, len(tails), text_count


def replay(records, lines, loki_url):
    timestamps = [int(record["timestamp"] * Decimal(1_000_000_000)) for record in records]
    shift = time.time_ns() - 5_000_000_000 - max(timestamps)
    values = [[str(ts + shift), line] for ts, line in zip(timestamps, lines)]
    payload = {"streams": [{"stream": LABELS, "values": values}]}
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = Request(
        loki_url.rstrip("/") + "/loki/api/v1/push",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"Loki respondió HTTP {response.status}")


def main():
    parser = argparse.ArgumentParser(description="Valida o reproduce la muestra original de ACARS en Loki.")
    parser.add_argument("--check", action="store_true", help="valida la muestra sin conectarse a la red")
    parser.add_argument("--loki-url", default="http://localhost:3100", help="URL base de Loki")
    parser.add_argument("--input", type=Path, default=SAMPLE, help="archivo JSONL de entrada (predeterminado: muestra original)")
    args = parser.parse_args()
    try:
        records, lines, tail_count, text_count = load_and_validate(args.input)
        if args.check:
            print(f"Muestra válida: {len(records)} registros, {tail_count} matrículas, {text_count} con texto.")
            return 0
        replay(records, lines, args.loki_url)
        print(f"Se enviaron {len(records)} registros a Loki ({args.loki_url.rstrip('/')}).")
        print('Consulta en Grafana: {job="acarsdec-demo"} en el rango Last 30 minutes.')
        print("La ingestión se desplazó al presente; el JSON original conserva su timestamp ACARS.")
        return 0
    except (ValueError, HTTPError, URLError, TimeoutError, RuntimeError, OSError) as exc:
        if isinstance(exc, HTTPError):
            message = f"Loki respondió HTTP {exc.code}: {exc.reason}"
        elif isinstance(exc, URLError):
            message = f"No se pudo conectar con Loki: {exc.reason}"
        else:
            message = str(exc)
        print(f"Error: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
