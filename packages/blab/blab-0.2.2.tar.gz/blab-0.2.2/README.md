# blab Tools for Jupyter
Some Jupyter Tools, see `jupyter` directory for examples

## Install
`pip install blab`

## Usage
Put this code in the first cell of your notebook:
```
# blab init
try:
    import blab
except ImportError as e:
    !pip install blab
    import blab    
startup_notebook = blab.blab_startup()
%run $startup_notebook  
```


## Features
blab is a collection of tools designed to enhance and streamline the Jupyter Notebook workflow. It provides two main categories of features: 
- Python functions available in the blab_tools.py module and
- functionalities enabled through a startup-notebook (blab_startup.ipynb by default)

### Python Functions (blab_tools.py) 
These functions are directly accessible after installing the blab library

#### run_notebooks()
Executes all Jupyter Notebooks (.ipynb) in the current directory in alphabetical order.
Supports different execution modes:
list: Lists the notebooks to be executed.
run: Executes notebooks and stops on the first error.
force: Executes all notebooks, ignoring errors.
Allows excluding notebooks via the exclude parameter.
Allows specifying an output directory with the out_dir parameter.
Allows setting a cell timeout with the cell_timeout parameter.
Prints the elapsed time for each notebook execution.

#### search_notebooks()
Performs a search for a string within Jupyter Notebooks and Python files.
Searches code cells, markdown cells, and output cells in notebooks.
Allows specifying the search scope with the radius parameter (current directory, parent directory, etc.).
Allows excluding files with the exclude parameter.
Allows specifying the file type with the suffix parameter (ipynb, py, etc.).
Prints the filenames of the files containing the search term.

#### help()
Displays the documentation of a Python object (function, class, etc.) in a formatted Markdown output within a Jupyter Notebook.
Interprets Markdown formatting in docstrings.
Uses inspect.signature() and inspect.getdoc(). 

### Startup Notebook Functionalities (blab_startup.ipynb) 
These features are enabled by running the blab_startup.ipynb notebook at the beginning of your Jupyter session:
- Automatic libs Folder Integration: Automatically detects a local folder named libs and adds it to the Python path. Enables easy use of private libraries within Jupyter Notebooks.
- Automatic Configuration:
    - Loads autoreload for automatic reloading of changed modules.
    - Loads ipytest for running tests within Jupyter Notebooks.
    - Configures %matplotlib inline for displaying plots directly in the notebook.

#### raise Stop
Ends the execution of a notebook and displays the elapsed time.

#### bgc()
Sets the background color of a notebook cell.

