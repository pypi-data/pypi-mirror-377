import pytest
import blab
import os

class TestBlabTools:

    def test_blab_startup_file_exists(self):
        """
        Tests if the blab_startup.ipynb file exists.
        """
        startup_notebook_path = blab.blab_startup()
        assert os.path.exists(startup_notebook_path)
        assert os.path.isfile(startup_notebook_path)
        assert startup_notebook_path.endswith(".ipynb")















