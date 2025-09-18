# datacontract_helper

howto:


```

build and publish:

```

manualy increase version in pyproject.toml and remove old version

 uv run python3 -m pip install --upgrade setuptools wheel

 uv run python3 -m build --no-isolation

 uv run twine upload --config-file ./.pypirc dist/*
 
 ```