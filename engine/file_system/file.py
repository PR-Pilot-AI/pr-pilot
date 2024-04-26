import logging

from .file_system_node import FileSystemNode

logger = logging.getLogger(__name__)


class File(FileSystemNode):

    @property
    def content(self) -> str:
        return self.path.read_text()

    def simple_dict(self, filter="") -> dict:
        """Return a simple dictionary representation of the node."""
        return {"path": str(self.path_relative_to_cwd)}
