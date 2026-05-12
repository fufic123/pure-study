import contextvars
import logging
import sys

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class _RidFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(service: str = "material", level: str = "DEBUG") -> None:
    fmt = logging.Formatter(
        fmt=f"%(asctime)s.%(msecs)03d [%(levelname)-5s] {service}.%(name)-20s rid=%(request_id)-12s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    handler.addFilter(_RidFilter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    for noisy in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
