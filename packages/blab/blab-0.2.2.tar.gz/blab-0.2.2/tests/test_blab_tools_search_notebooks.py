
import pytest
import blab
import os
import shutil
import warnings
import glob
import pathlib
import functools

def find_jupyter_dir(start_path):
    """
    Recursively searches for the 'jupyter' directory in the parent directories.
    """
    current_path = start_path
    while current_path != current_path.parent:  # Stop at the root directory
        jupyter_path = current_path / 'jupyter'
        if jupyter_path.is_dir():
            return jupyter_path
        current_path = current_path.parent
    return None  # 'jupyter' directory not found


def chdir_jupyter(func):
    """
    Decorator to change the current directory to the 'jupyter' directory before
    running a test and change back to the original directory afterwards.
    It searches for the 'jupyter' directory by going up the parent directories.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_dir = os.getcwd()
        jupyter_dir = find_jupyter_dir(pathlib.Path(__file__).parent)
        if jupyter_dir is None:
            raise FileNotFoundError("Could not find 'jupyter' directory in any parent directory.")
        os.chdir(jupyter_dir)
        shutil.rmtree("nb_out", ignore_errors=True)
        try:
            result = func(*args, **kwargs)
        finally:
            shutil.rmtree("nb_out", ignore_errors=True)
            os.chdir(current_dir)
        return result
    return wrapper


# --------------------------------------------------------------------------------------------
class TestBlabToolsSearchNotebooks:

    @chdir_jupyter
    def test_search_notebooks_finds_multiple_queries_in_existing_notebooks(self, capsys):
        """Tests if search_notebooks finds multiple queries in existing notebooks."""
        # Assuming 70_dummy_notebook_one.ipynb contains "Hello 1"
        # and 80_dummy_notebook_two.ipynb contains "Hello 2"
        blab.search_notebooks("Hello 1", radius=0)
        captured = capsys.readouterr()
        assert "70_dummy_notebook_one.ipynb" in captured.out

        blab.search_notebooks("Hello 2", radius=0)
        captured = capsys.readouterr()
        assert "80_dummy_notebook_two.ipynb" in captured.out


    @chdir_jupyter
    def test_search_notebooks_exclude(self, capsys):
        """Tests if search_notebooks excludes files correctly."""
        blab.search_notebooks("Hello", radius=0, exclude=["one"])
        captured = capsys.readouterr()
        assert "70_dummy_notebook_one.ipynb" not in captured.out
        assert "80_dummy_notebook_two.ipynb" in captured.out

    @chdir_jupyter
    def test_search_notebooks_radius_1_finds_in_readme(self, capsys):
        """Tests if search_notebooks with radius=1 finds the query in README.ipynb."""
        blab.search_notebooks("install", radius=1)
        captured = capsys.readouterr()
        assert "../README.ipynb" in captured.out