import logging
import sys


def setup_logging(service: str = "auth", level: str = "DEBUG") -> None:
    fmt = logging.Formatter(
        fmt=f"%(asctime)s.%(msecs)03d [%(levelname)-5s] {service}.%(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
