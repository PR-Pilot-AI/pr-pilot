import logging
from pathlib import Path
from typing import List, Optional

from django.conf import settings
from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)


class FileSystemNode(BaseModel):
    """Represents a file in the file system."""

    path: Path = Field(description="Path of the node in the file system")
    nodes: List["FileSystemNode"] = Field(
        description="List of files and directories in the directory", default=[]
    )
    parent: Optional["FileSystemNode"] = Field(
        description="Parent directory", default=None
    )

    @property
    def path_relative_to_cwd(self):
        return self.path.relative_to(settings.REPO_DIR)

    @property
    def is_directory(self):
        return self.path.is_dir()

    @property
    def is_file(self):
        return self.path.is_file()

    def simple_dict(self, filter="") -> dict:
        """Return a simple dictionary representation of the node."""
        raise NotImplementedError
