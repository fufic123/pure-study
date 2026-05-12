from app.sources.base import BaseSource
from app.sources.mit_ocw import MITOCWSource
from app.sources.wikipedia import WikipediaSource

_SOURCES: dict[str, BaseSource] = {
    "mit_ocw": MITOCWSource(),
    "wikipedia": WikipediaSource(),
}


def get_source(source_id: str) -> BaseSource:
    source = _SOURCES.get(source_id)
    if not source:
        raise KeyError(f"Unknown source '{source_id}'. Available: {list(_SOURCES)}")
    return source


def list_sources() -> list[dict]:
    return [
        {"id": s.source_id, "name": s.display_name}
        for s in _SOURCES.values()
    ]
