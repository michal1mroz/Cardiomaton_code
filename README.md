# Cardiomaton - project repository

## Starting application
This section explains the requirements of the Cardiomaton application as well as a method to start it.

### Requirements
Cardiomaton app requires following dependencies:
* Python - version 3.11 or higher
* Poetry - version 2.0.0 or higher
* C compiler - GNU compiler for Linux, Visual Studio build tools for C++ for Windows

### Starting application
Application can be started by running correct scripts - `cardiomaton.bat` for windows, or `cardiomaton.sh` for linux or macOS.
Alternatively, to manually build and start the project run the following commands from the root of the project:
```shell
eval $(poetry env activate)
poetry run build
cd cardiomaton_code
python main_with_front.py
```

## Setup information for development

### Poetry installation:
Dependencies should be added to poetry with
```shell
poetry add <package_name>
```
and then installed.

To use the jupyter with poetry environment first create the poetry venv and then add the new kernel with venv set to the path of the poetrys venv (for linux it's typically ~/.cache/pypoetry/virtualenvs/<cardiomaton...>/bin/<python_interperter_version>).

### Creating default database:
Right now program uses the database to load the automaton. To create the default database entry for the database please run `populate_db.py` script with:
```shell
python populate_db.py
```

### Compiling cython modules:
Before the program can be run all cython modules need to be compiled. To do so use provided scripts with the command:
```shell
poetry run build
```
To remove generated files (.c, .so files) run
```shell
poetry run clean
```


