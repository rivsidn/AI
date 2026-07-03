#!/usr/bin/env python3
"""Open a Freeplane map and capture a screenshot for visual inspection."""

from __future__ import annotations

import argparse
import os
import signal
import shutil
import subprocess
import time
from pathlib import Path


def capture(args: argparse.Namespace) -> int:
    try:
        from PIL import ImageGrab
    except Exception as exc:  # pragma: no cover - depends on local GUI stack
        raise SystemExit(f"Pillow ImageGrab is required for screenshots: {exc}") from exc

    map_path = Path(args.map).expanduser().resolve()
    if not map_path.exists():
        raise SystemExit(f"Map does not exist: {map_path}")
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [args.freeplane, str(map_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    time.sleep(args.wait)
    if shutil.which("wmctrl"):
        subprocess.run(["wmctrl", "-a", map_path.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(args.focus_wait)
    image = ImageGrab.grab()
    image.save(output)
    print(f"Saved screenshot: {output}")

    if args.keep_open:
        print(f"Freeplane left open with pid {proc.pid}")
        return 0
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=3)
    except ProcessLookupError:
        pass
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", help="Freeplane .mm file to open")
    parser.add_argument("output", help="Screenshot PNG path")
    parser.add_argument("--wait", type=float, default=7.0, help="Seconds to wait before capturing")
    parser.add_argument("--focus-wait", type=float, default=1.0, help="Seconds to wait after focusing the Freeplane window")
    parser.add_argument("--freeplane", default="freeplane", help="Freeplane executable")
    parser.add_argument("--keep-open", action="store_true", help="Do not close Freeplane after capturing")
    return parser


def main() -> int:
    return capture(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
