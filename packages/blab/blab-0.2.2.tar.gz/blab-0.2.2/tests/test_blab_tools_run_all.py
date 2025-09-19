
import pytest
import blab
import os
import shutil
import warnings
from nbconvert.preprocessors import CellExecutionError
from nbformat.validator import ValidationError
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
class TestBlabToolsRunAll:

    @chdir_jupyter
    def test_run_notebooks_list(self,capsys):
        """Tests run_notebooks in list mode."""
        blab.run_notebooks(mode="list", exclude=['99', '40'])
        captured = capsys.readouterr()
        assert "70_dummy_notebook_one.ipynb" in captured.out
        assert "80_dummy_notebook_two.ipynb" in captured.out
        assert "99_Run_all_notebooks_in_this_folder.ipynb" not in captured.out
        assert "40_raise_Stop.ipynb" not in captured.out
        assert "40" not in captured.out
        assert "99" not in captured.out
        assert "Trying to run this" in captured.out


    @chdir_jupyter
    def test_run_notebooks_run_success(self):
        """Tests run_notebooks in run mode with successful execution."""
        blab.run_notebooks(mode="run", exclude=['99', '40','my_startup'])
        assert os.path.exists("nb_out/70_dummy_notebook_one.ipynb")
        assert os.path.exists("nb_out/80_dummy_notebook_two.ipynb")
        assert not os.path.exists("nb_out/99_Run_all_notebooks_in_this_folder.ipynb")
        assert not os.path.exists("nb_out/40_raise_Stop.ipynb")


    @chdir_jupyter
    def test_run_notebooks_run_error(self):
        """Tests run_notebooks in run mode with an error."""
        with pytest.raises((CellExecutionError, ValidationError)):
            blab.run_notebooks(mode="run", exclude=['10','20','50','99','my_startup'])


    @chdir_jupyter
    def test_run_notebooks_force_mode_error(self):
        """Tests run_notebooks in force mode with an error."""
        with warnings.catch_warnings(record=True) as w:
            blab.run_notebooks(mode="force", exclude=['10','20','50','99'])
            assert len(w) >= 1
            assert "Error executing the notebook" in str(w[0].message)
        assert os.path.exists("nb_out/70_dummy_notebook_one.ipynb")
        assert os.path.exists("nb_out/80_dummy_notebook_two.ipynb")
        assert os.path.exists("nb_out/40_raise_Stop.ipynb")
        assert not os.path.exists("nb_out/99_Run_all_notebooks_in_this_folder.ipynb")



    @chdir_jupyter
    def test_run_notebooks_out_dir(self):
        """Tests run_notebooks with the out_dir option."""
        shutil.rmtree("my_test_output", ignore_errors=True)
        blab.run_notebooks(mode="run", out_dir="my_test_output/", exclude=['10','20','50','99', '40','my_startup'])
        assert os.path.exists("my_test_output/70_dummy_notebook_one.ipynb")
        assert os.path.exists("my_test_output/80_dummy_notebook_two.ipynb")
        shutil.rmtree("my_test_output", ignore_errors=True)





