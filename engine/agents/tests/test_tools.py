import os
import tempfile

import pytest

from engine.agents.pr_pilot_agent import list_directory


@pytest.mark.django_db
def test_list_directories(task):
    # Create temp dir
    temp_dir = tempfile.TemporaryDirectory()
    # Add three distinct, empty files
    files = ["file1.yaml", "file2.py", "subdir.py"]
    # Create directory called subdir in temp dir
    temp_dir_name = temp_dir.name
    subdir = f"{temp_dir_name}/subdir"
    os.mkdir(subdir)
    # Create the files in subdir
    for file in files:
        open(f"{subdir}/{file}", "w").close()

    # List the directories
    from django.conf import settings

    settings.REPO_DIR = temp_dir_name
    markdown_result = list_directory.invoke("subdir")
    assert (
        markdown_result.strip()
        == """Content of `subdir`:

- file1.yaml
- file2.py
- subdir.py
""".strip()
    )
