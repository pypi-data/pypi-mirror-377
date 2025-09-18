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


Как добавить пакет с send_to_kafka и классом для DTO в код:

```BASH
uv add "service-example" --default-index https://nexus.k8s-analytics.ostrovok.in/repository/datacontract_pypi/simple --extra-index-url https://pypi.org/simple/ 

```