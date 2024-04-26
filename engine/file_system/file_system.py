import logging
import os
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Set, Optional

import yaml
from django.conf import settings

from .directory import Directory
from .file import File
from .file_system_node import FileSystemNode

logger = logging.getLogger(__name__)


class FileSystem:
    """Utility class for file system operations."""

    def __init__(self, root_directory=None):
        if not root_directory:
            root_directory = Path(settings.REPO_DIR)
        self.root_directory = root_directory
        if not self.root_directory.exists():
            raise FileNotFoundError(
                f"Root directory '{self.root_directory}' does not exist."
            )
        self.root_directory = self.root_directory
        self.tree = self._build_tree(self.root_directory)

    def yaml(self, filter="") -> str:
        """Walk through tree in-order and collect paths of all files and directories."""
        return yaml.safe_dump(self.tree.simple_dict(filter))

    @property
    def ignore_list(self) -> Set[str]:
        if not hasattr(self, "_ignore_list"):
            # Create file if it doesn't exist
            if not os.path.exists(settings.IGNORE_FILE_PATH):
                default_ignore_content = Path(
                    os.path.join(os.path.dirname(__file__), "default_ignore.txt")
                ).read_text()
                with open(settings.IGNORE_FILE_PATH, "w") as f:
                    f.write(default_ignore_content)
            with open(settings.IGNORE_FILE_PATH, "r") as f:
                self._ignore_list = set(f.read().splitlines())
        return self._ignore_list

    def _build_tree(self, path: Path, parent: FileSystemNode = None) -> FileSystemNode:
        """Recursively build a directory tree starting from the given path."""
        if path.is_dir():
            node = Directory(path=path, parent=parent)
        else:
            node = File(path=path, parent=parent)
        for item in path.iterdir():
            if self.should_be_ignored(item):
                continue
            if item.is_dir():
                node.nodes.append(self._build_tree(item, node))
            else:
                node.nodes.append(File(path=item, parent=node))
        return node

    def should_be_ignored(self, path) -> bool:
        """Check if the given path should be ignored, respecting .gitignore-style patterns."""
        if isinstance(path, str):
            path = Path(path)
        if path.is_absolute():
            relative_path = str(path.relative_to(settings.REPO_DIR)).rstrip("/")
        else:
            relative_path = str(path).rstrip("/")

        # Iterate over each pattern in the ignore list
        for pattern in self.ignore_list:
            # Check if the pattern matches the entire directory (including subdirectories and files)
            if (
                relative_path.startswith(pattern.rstrip("/") + "/")
                or relative_path == pattern
            ):
                return True

            # Check both the file/directory name and the relative path against the ignore patterns
            if fnmatch(path.name, pattern) or fnmatch(relative_path, pattern):
                return True

        return False

    def get_directory_tree(self) -> List[dict]:
        """Build a directory tree from the root using the pre-built tree."""
        return self._build_tree_dict(self.tree)

    def _build_tree_dict(self, node: FileSystemNode, parent_path="") -> List[dict]:
        tree = []
        for child in node.nodes:
            relative_path = os.path.join(parent_path, child.path.name)
            if child.is_directory:
                tree.append(
                    {
                        "id": relative_path,
                        "text": child.path.name,
                        "type": "default",
                        "children": self._build_tree_dict(child, relative_path),
                    }
                )
            else:
                tree.append(
                    {
                        "id": relative_path,
                        "text": child.path.name,
                        "type": "file",
                    }
                )
        return tree

    def list_files(self) -> List[Path]:
        """List all files in the tree, excluding ignored files."""
        return self._list_files_recursive(self.tree)

    def _list_files_recursive(self, node: FileSystemNode) -> List[Path]:
        files_list = []
        for child in node.nodes:
            if child.is_directory:
                files_list.extend(self._list_files_recursive(child))
            else:
                files_list.append(child.path)
        return files_list

    def get_node(self, path: Path) -> Optional[FileSystemNode]:
        """Get the node at the given path."""
        if not path.is_absolute():
            path = self.root_directory / path
        return self._get_node_recursive(self.tree, path)

    def _get_node_recursive(
        self, tree: FileSystemNode, path: Path
    ) -> Optional[FileSystemNode]:
        """Recursively get the node at the given path."""
        if tree.path == path:
            return tree
        for node in tree.nodes:
            if node.path == path:
                return node
            if node.is_directory:
                result = self._get_node_recursive(node, path)
                if result:
                    return result
        return None

    def save(self, content: str, path: Path) -> FileSystemNode:
        """
        Save the given content to the given path.
        :param content: Content to save
        :param path: Path to save to
        :return: File node
        """
        absolute_path = path
        if not path.is_absolute():
            absolute_path = self.root_directory / path
        if absolute_path.is_dir():
            raise ValueError(f"Cannot save content to directory `{absolute_path}`.")
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(content)
        self.tree = self._build_tree(self.root_directory)
        return self.get_node(path)

    def create_directory(self, path):
        absolute_path = self.root_directory / path
        absolute_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created: {absolute_path}")

    def move_file(self, source, destination):
        source = self.root_directory / source
        destination = self.root_directory / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
        logger.info(f"File moved from {source} to {destination}")

    def copy_file(self, source, destination):
        source = self.root_directory / source
        destination = self.root_directory / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text())
        logger.info(f"File copied from {source} to {destination}")

    def delete_file(self, path):
        path = self.root_directory / path
        path.unlink()
        logger.info(f"File deleted: {path}")


if __name__ == "__main__":
    file_system = FileSystem()
    yaml_str = file_system.yaml()
    print(yaml_str)
