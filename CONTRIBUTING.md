To get started contributing to this project, you'll first need to set up your development environment.

```
git clone https://github.com/alphachainio/alchemy_sdk_py
cd alchemy_sdk_py

python3 -m venv venv
source venv/bin/activate
```

We set up a virtual environment so that packages you install get installed to an isolated location (the `venv` folder we just created). If you want to exit this virtual environment, you can run `deactivate`.

Then, install the development dependencies.

```
pip install -r requirements-dev.txt
```

### Optional

You can also install the package in editable mode.

```
pip install -e .
```

The `pip install -e .` command installs our package in "editable" mode. This means that any changes you make to the code will be reflected in the package you import in your own code.

This would be if you want to run make changes and test them out on your own code in another project. 


## Testing

Then, run the tests to make sure everything is working:

```
pytest
```