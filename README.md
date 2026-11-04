# Gestor de Proyectos

Aplicacion de escritorio para administrar proyectos y sus servicios locales,
desarrollada con Python y PySide6.

## Requisitos

- Python 3.10 o superior
- Dependencias listadas en `requisitos.txt`

## Instalacion

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requisitos.txt
```

## Ejecucion

```powershell
python main.py
```

La base de datos se crea automaticamente en
`%USERPROFILE%\.gestor_proyectos\proyectos.db`.
