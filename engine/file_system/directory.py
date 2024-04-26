import logging

from .file_system_node import FileSystemNode

logger = logging.getLogger(__name__)


class Directory(FileSystemNode):

    def simple_dict(self, filter="") -> dict:
        """Return a simple dictionary representation of the node."""
        files = [
            str(child.path).replace(str(child.parent.path), "").lstrip("/")
            for child in self.nodes
            if child.is_file
        ]
        if filter:
            files = [file for file in files if filter in file]
        dirs = [child.simple_dict(filter) for child in self.nodes if child.is_directory]
        dirs = [dir for dir in dirs if dir]
        all_items = files + dirs
        if not all_items:
            return None
        return {str(self.path_relative_to_cwd): all_items}
