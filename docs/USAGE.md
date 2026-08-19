# Usage Guide

## First-time setup

Run the model setup script from PowerShell:

```powershell
.\scripts\setup_models.ps1
```

Create the environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` when you want to customize models or paths.

## Start the application

```powershell
.\scripts\run_local.ps1
```

Open [http://localhost:8501](http://localhost:8501).

## Index documents

Upload PDF, TXT, or Markdown files in the interface and select **Prepare documents**. Files already placed in `documents/` can be processed with **Rescan folder**.

## Stop local services

```powershell
.\scripts\stop_local.ps1
```

This stops listeners on ports `8501` and `11434`. It does not delete documents, models, or the vector database.
