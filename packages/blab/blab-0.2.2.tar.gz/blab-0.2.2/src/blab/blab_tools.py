
import warnings, datetime, inspect
import bpyth as bpy
from IPython.display import Markdown
from nbformat.validator import ValidationError

#############################################################################################################
### blab_startup
#############################################################################################################

def blab_startup():
    """
    Returns the path to the default startup notebook.

    This function retrieves the file path of the `blab_startup.ipynb` notebook,
    which contains essential configurations and initializations for using the
    `blab` library within a Jupyter Notebook environment.

    **Returns:**
    - `str`: The file path to the `blab_startup.ipynb` notebook.

    **Example:**
    To initialize `blab` in a Jupyter Notebook, use the following code in the
    first cell:
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

    """
    from importlib_resources import files
    notebook = str(files('blab').joinpath('blab_startup.ipynb'))
    return notebook





#############################################################################################################
### run_notebooks
#############################################################################################################

# https://nbconvert.readthedocs.io/en/latest/execute_api.html
def run_notebooks( exclude=[], out_dir = 'nb_out/', mode='list', cell_timeout=None  ):
    '''
    Executes Jupyter Notebooks in the current directory using nbconvert.

    This function iterates through all Jupyter Notebook files (`.ipynb`) in the
    current directory, executes them sequentially in alphabetical order, and
    saves the executed notebooks to an output directory.

    **Args:**
    - `exclude (list of str, optional)`: A list of strings. Notebook filenames
            containing any of these strings will be excluded from execution.
            Defaults to None (no files excluded).
    - `out_dir (str, optional)`: The directory where the executed notebooks
            will be saved. If the directory does not exist, it will be created.
            Defaults to 'nb_out/'.
    - `mode (str, optional)`: Specifies the execution mode.
        - `list`: Only lists the notebooks that would be executed. (Default)
        - `run`: Executes the notebooks and stops on the first error.
        - `force`: Executes all notebooks, ignoring errors.
    - `cell_timeout` (int, optional): The maximum execution time (in seconds)
            allowed for each cell. If a cell exceeds this timeout, a
            CellExecutionError will be raised. If None, no timeout is applied.
            Defaults to None.

    **Returns:**
        None

    **Raises:**
        CellExecutionError: If a cell in a notebook fails to execute and the
            mode is set to 'run'.

    **Notes:**
    - The notebooks are executed in the order they appear when sorted
      alphabetically.
    - The original notebooks are not modified. The executed notebooks are
      saved as new files in the out_dir.
    - If a notebook execution fails in 'force' mode, a warning is issued,
      but the execution continues with the next notebook.
    - The elapsed time for each notebook execution is printed to the console.
    - The function prints a list of the notebooks that will be executed
      before starting the execution.

    **Examples:**
    - To list the notebooks that would be executed:
        `run_notebooks()`
    - To execute all notebooks and stop on the first error:
        `run_notebooks(mode='run')`
    - To execute all notebooks, ignoring errors:
        `run_notebooks(mode='force')`
    - To exclude notebooks containing 'draft' in their filename:
        `run_notebooks(exclude=['draft'], mode='run')`
    - To set a timeout of 60 seconds for each cell:
        `run_notebooks(mode='run', cell_timeout=60)`
    - To save the executed notebooks in a different directory:
        `run_notebooks(out_dir='my_notebooks/', mode='run')`
    '''
    
    import os   
    
    # exclude: force list
    if isinstance(exclude, str):
        exclude = [exclude]
    
    # Create
    if not os.path.exists(out_dir):
        os.makedirs(out_dir) 
    
    # List Files
    notebooks = [ f for f in os.listdir('.') if os.path.isfile( os.path.join('.', f))]
    notebooks = [ d for d in notebooks if d.endswith('ipynb') ]
    notebooks = [s for s in notebooks if not any(x in s for x in exclude)]
    notebooks = sorted(notebooks)
    
    print('Trying to run this {} notebooks:'.format(len(notebooks)))
    for nbf in notebooks:
        print('         {:<40}'.format(nbf)) 
    print()
    if not mode in ['run','force']:
        print("Set mode='run' or mode='force' to run these notebooks.")
        return
    
    # Run
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
    ep = ExecutePreprocessor(timeout=cell_timeout)

    for nbfile in notebooks:

        # öffnen
        with open(nbfile, encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        #print('Starting', nbfile)
        print('         {:<40}'.format(nbfile), end='   ')

        # ausführen
        startzeit = datetime.datetime.now()
        try:
            ep.preprocess(nb)
        except (CellExecutionError, ValidationError):
            msg = 'Error executing the notebook "%s"\n\n' % nbfile
            warnings.warn(msg)
            if mode != 'force':
                raise        
        finally:
            # Ergebnis abspeichern
            stopzeit = datetime.datetime.now()
            difference = stopzeit - startzeit
            print( ' ', bpy.human_readable_seconds(difference.seconds)  )
            with open( out_dir + nbfile, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)  
            
    # Ende for
    print('='*60, '\n\n')


    
    
#############################################################################################################
### search_code
#############################################################################################################    

def search_notebooks( query, radius=1, exclude=[], suffix='ipynb'):
    """
    Searches for a string within Jupyter Notebooks and Python files.

    This function performs a case-sensitive search for a given string (`query`)
    within the content of Jupyter Notebook files (`.ipynb`) and/or Python files
    (`.py`). The search encompasses code cells, markdown cells, and output cells
    in notebooks, as well as the content of Python files.

    **Args:**
    - `query (str)`: The string to search for. The search is case-sensitive.
    - `radius (int, optional)`: Specifies the search scope relative to the
            current directory.
        - 0: Search only in the current directory.
        - 1: Search in the parent directory and all its subdirectories
          (one level up).
        - n: Search n levels up and all their subdirectories, respectively.
        Defaults to 1.
    - `exclude (list of str, optional)`: A list of strings. Filenames
            containing any of these strings will be excluded from the search.
            Defaults to None (no files excluded).
    - `suffix (str, optional)`: The file suffix to search for.
        - 'ipynb': Search only in Jupyter Notebook files (default).
        - 'py': Search only in Python files.
        - Any other string: Search for files with that suffix.

    **Returns:**
        None (the function prints the filenames of the files containing the query)

    **Example:**
    - To search for "my_variable" in all notebooks in the current directory:<br>
      `search_notebooks("my_variable", radius=0)`

    - To search for "my_class" only in Python files in the current directory and
        in the parent directory:<br>
        `search_notebooks("my_class", suffix="py")`

    - To search for "X3f" in all notebooks up to two levels up, excluding files
        containing "old":<br>
        `search_notebooks("X3f", radius=2, exclude=["old"])`
    """
    
    # exclude: force list
    if isinstance(exclude, str):
        exclude = [exclude]    
    
    import glob
    def suche_intern(query,pattern):
        result = []
        for filepath in glob.iglob(pattern, recursive=True):
            with open(filepath) as file:
                try:
                    s = file.read()
                    if (s.find(query) > -1):
                        result.append(filepath)
                except:
                    pass
        return result
    # ende suche_intern
                
    result = []
    if (radius == 0):
        pattern = '*.' + suffix
    elif (radius == 1):
        pattern = '../**/*.' + suffix
    elif (radius == 2):
        pattern = '../../**/*.' + suffix   
    elif (radius == 3):
        pattern = '../../../**/*.' + suffix    
    elif (radius == 4):
        pattern = '../../../../**/*.' + suffix
    else:
        pattern = '../../../../../**/*.ipynb'              
    result += suche_intern(query,pattern)
    
    result += ['----------------------------------']
    if (radius == 0):
        pattern = '*.py'
    else:
        pattern = '../**/*.py'
    result += suche_intern(query,pattern)
    
    result = [s for s in result if not any(x in s for x in exclude)]
    
    # Ausgabe
    if len(result) < 1:
        print('Nothing found')
    else:
        for r in result:
            print(r)
    #return result
    
    
    
#############################################################################################################
### help in Markdown
#############################################################################################################     

def help(obj):
    '''
    Displays the documentation of a Python object in a formatted Markdown output within a Jupyter Notebook.

    This function is designed to enhance the documentation experience within
    Jupyter Notebooks. It retrieves the signature and docstring of a given
    Python object (e.g., a function, class, or method) using the `inspect`
    module, interprets any Markdown formatting within the docstring, and
    displays the formatted documentation in the notebook.

    This allows developers to write rich, formatted documentation using Markdown
    within their docstrings, which can then be easily viewed and rendered
    directly within the notebook environment.

    **Args:**
    - obj (object): The Python object for which to display documentation.
        This can be a function, class, method, module, or any other
        inspectable Python object.

    **Returns:**
    - IPython.display.Markdown: The formatted documentation as a Markdown object,
        which is automatically rendered by Jupyter Notebook.

    **Notes:**
    - The function uses `inspect.signature()` to retrieve the object's
      signature and `inspect.getdoc()` to retrieve its docstring.

    **Examples:**
    - To display the documentation for the search_notebooks function:
      `help(search_notebooks)`
    - To display the documentation for the run_notebooks function:
        `help(run_notebooks)`
    - To display the documentation for the help function itself:
        `help(help)`
    '''
    signature = ''
    doc = ''
    try:
        signature = str(inspect.signature(obj))
    except:
        pass
    try:
        doc = inspect.getdoc(obj)
    except:
        pass
    result = '<span style="font-size:larger; margin-top: 15px; display: block;">' + \
             '**' + obj.__name__ + '**' + \
             signature + ':</span>' + '\n\n' + doc
    result = Markdown(result)
    # print(Markdown)
    return display(result)

render_doc = help