# Cardiomaton - project repository

## Setup information

### Poetry installation:
Dependencies should be added to poetry with
```shell
poetry add <package_name>
```
and then installed.

To use the jupyter with poetry environment first create the poetry venv and then add the new kernel with venv set to the path of the poetrys venv (for linux it's typically ~/.cache/pypoetry/virtualenvs/<cardiomaton...>/bin/<python_interperter_version>).

### Compiling cython modules:
Before the program can be run all cython modules need to be compiled. To do so use provided scripts with the command:
```shell
poetry run build
```
To remove generated files (.c, .so files) run
```shell
poetry run clean
```


