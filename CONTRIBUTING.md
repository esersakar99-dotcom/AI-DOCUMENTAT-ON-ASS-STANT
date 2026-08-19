# Contributing

## Development setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Pull the models listed in the README.
4. Create a focused branch from `main`.

## Before opening a pull request

```powershell
python -m unittest discover -v
python -m compileall -q app.py src tests
```

Keep commits focused and use imperative, descriptive commit messages. Do not commit documents, vector databases, model files, logs, or virtual environments.
