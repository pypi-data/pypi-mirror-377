```
python -m pip install --upgrade pip build twine
python -m build
twine upload -r testpypi dist/*
twine upload -r pypi dist/*
```