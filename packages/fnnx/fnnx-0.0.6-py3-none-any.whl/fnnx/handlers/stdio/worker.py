from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from fnnx.runtime import Runtime
from fnnx.handlers.local import LocalHandler
from fnnx.device import DeviceMap

try:
    from fnnx.dtypes import NDContainer  # type: ignore
except Exception:
    NDContainer = None  # type: ignore
try:
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover
    _np = None


class StdIOServer:
    def __init__(self, handlers: dict[str, Callable], num_threads: int = 1):
        self.handlers = handlers
        self.num_threads = num_threads
        self.executor = ThreadPoolExecutor(max_workers=num_threads)

    def _inner(self, line: str):
        try:
            req = json.loads(line)
            rid = req["id"]
            handler = req["handler"]
            body = req["body"]

            if handler not in self.handlers:
                raise ValueError(f"Unknown handler {handler}")

            result = self.handlers[handler](body)
            print(
                json.dumps(
                    {
                        "id": rid,
                        "body": result,
                        "status": "ok",
                        "type": "fnnx_stdio_response",
                    }
                ),
                flush=True,
            )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "id": rid,
                        "error": f"{str(e.__class__.__name__)}({str(e)})",
                        "status": "error",
                        "type": "fnnx_stdio_response",
                    }
                ),
                flush=True,
            )

    def loop(self):
        for line in sys.stdin:
            self.executor.submit(self._inner, line)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to the FNNX model bundle")
    p.add_argument(
        "--device-map",
        default=None,
        help=(
            "JSON-encoded DeviceMap "
            "(keys: accelerator, node_device_map, variant_device_config)"
        ),
    )
    p.add_argument(
        "--worker-num-threads",
        type=int,
        default=1,
        help="Number of threads to use in the worker",
    )
    return p.parse_args()


def _to_jsonable(o):
    out = {}
    for k, v in o.items():
        if _np is not None and isinstance(v, _np.ndarray):
            out[k] = v.tolist()
        elif NDContainer is not None and isinstance(v, NDContainer):
            out[k] = v.data
        else:
            out[k] = v
    return out


def main():
    args = _parse_args()
    _device_map_obj = None
    if args.device_map:
        try:
            dm = json.loads(args.device_map)
            _device_map_obj = DeviceMap(
                accelerator=dm.get("accelerator", "cpu"),
                node_device_map=dm.get("node_device_map", {}) or {},
                variant_device_config=dm.get("variant_device_config", None),
            )
        except Exception as e:
            print(f"Failed to parse --device-map: {e}", file=sys.stderr)
            sys.exit(2)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runtime = Runtime(
        args.model,
        handler=LocalHandler,
        handler_config=None,
        device_map=_device_map_obj,
        cleanup=False,
    )

    def rt_compute(body: dict):
        inputs = body.get("inputs", {})
        dynamic_attributes = body.get("dynamic_attributes", {}) or {}

        result = runtime.compute(inputs, dynamic_attributes)
        return _to_jsonable(result)

    def rt_compute_async(body: dict):
        inputs = body.get("inputs", {})
        dynamic_attributes = body.get("dynamic_attributes", {}) or {}

        result = loop.run_until_complete(
            runtime.compute_async(inputs, dynamic_attributes)
        )
        return _to_jsonable(result)

    StdIOServer(
        {"compute": rt_compute, "compute_async": rt_compute_async},
        num_threads=args.worker_num_threads,
    ).loop()


if __name__ == "__main__":
    print("Starting FNNX StdIO worker", flush=True)
    import os

    print(os.getenv("FNNX_PASS_TEST", "not set"), flush=True)
    main()
