from .plone import MetadataInfo
from .plone import PloneItem
from .plone import PloneItemGenerator
from .settings import TransmuteSettings
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from rich.progress import Progress
from typing import Any
from typing import TypedDict


__all__ = [
    "ItemProcessor",
    "PipelineItemReport",
    "PipelineProgress",
    "PipelineState",
    "PipelineStep",
    "ReportProgress",
    "ReportState",
]


@dataclass
class PipelineProgress:
    processed: Progress
    processed_id: str
    dropped: Progress
    dropped_id: str

    def advance(self, task: str) -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.advance(task_id)

    def total(self, task: str, total: int) -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.update(task_id, total=total)


@dataclass
class ReportProgress:
    processed: Progress
    processed_id: str

    def advance(self, task: str = "processed") -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.advance(task_id)


@dataclass
class PipelineItemReport(TypedDict):
    filename: str
    src_path: str
    src_uid: str
    src_type: str
    dst_path: str
    dst_uid: str
    dst_type: str
    last_step: str


@dataclass
class PipelineState:
    total: int
    processed: int
    exported: defaultdict[str, int]
    dropped: defaultdict[str, int]
    progress: PipelineProgress = field(repr=False)
    seen: set = field(default_factory=set, repr=False)
    uids: dict = field(default_factory=dict, repr=False)
    uid_path: dict = field(default_factory=dict, repr=False)
    path_transforms: list[PipelineItemReport] = field(default_factory=list, repr=False)
    paths: list[tuple[str, str, str]] = field(default_factory=list, repr=False)
    post_processing: dict[str, list[str]] = field(default_factory=dict, repr=False)
    annotations: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)
    metadata: MetadataInfo | None = field(default=None, repr=False)


@dataclass
class ReportState:
    files: Iterator
    types: defaultdict[str, int]
    creators: defaultdict[str, int]
    states: defaultdict[str, int]
    subjects: defaultdict[str, int]
    layout: dict[str, defaultdict[str, int]]
    type_report: defaultdict[str, list]
    progress: PipelineProgress

    def to_dict(self) -> dict[str, int | dict]:
        """Return report as dictionary."""
        data = {}
        for key in ("types", "creators", "states", "layout", "subjects"):
            value = getattr(self, key)
            data[key] = value
        return data


PipelineStep = Callable[
    [PloneItem, PipelineState, TransmuteSettings], PloneItemGenerator
]

ItemProcessor = Callable[[PloneItem, PipelineState], PloneItem]
