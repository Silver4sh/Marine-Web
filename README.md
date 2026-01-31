# Marine-Web Project

Welcome to the MarineOS Web Project. This repository contains two versions of the dashboard application:

## 🚀 1. HTMX Application (`/htmx`)
The **modern, high-performance** web application.
- **Stack**: FastAPI, HTMX, Tailwind CSS.
- **Use Case**: Primary production dashboard, customer facing.
- **Run**: `python -m uvicorn htmx.main:app --reload`
- [Read Docs](htmx/README.md)

## 🐢 2. Streamlit Application (`/streamlit`)
The **legacy/prototype** application.
- **Stack**: Streamlit (Python).
- **Use Case**: Internal tools, quick prototyping, reference.
- **Run**: `streamlit run streamlit/main.py`
- [Read Docs](streamlit/README.md)