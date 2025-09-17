# hnt_sap_library


# Reglas de negócios para os script SAP: 
Obtem dados do fornecedor SAP:

## Contrato
    - Dados do Fornecedor (XK03, ME3L)

# Requirements
    Pip 24.0
    Python 3.11.5
    VirtualEnv

# Setup the development env unix
```sh
virtualenv venv
. ./venv/bin/activate
```

# Setup the development env win10
```sh
python -m venv venv
. .\venv\Scripts\activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python.exe -m pip install --upgrade pip
pip install pytest
pip install python-dotenv
pip install robotframework-sapguilibrary
copy .\.env.template .\.env
```

# Before publish the packages
```sh
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install twine
```
# How to cleanup generated files to publish
```powershell
Remove-Item .\build\ -Force -Recurse
Remove-Item .\dist\ -Force -Recurse
Remove-Item .\hnt_sap_fornecedor_library.egg-info\ -Force -Recurse
```

# How to publish the package to test.pypi.org
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

# How to publish the package to pypi.org (username/password see lastpass Pypi)
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```
