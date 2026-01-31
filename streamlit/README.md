# Marine-Web (Legacy Streamlit)

This is the **Legacy** version of the MarineOS Dashboard, built with **Streamlit**. It is maintained for reference and backward compatibility.

## Architecture
- **Framework**: Streamlit
- **Database**: PostgreSQL (via `sqlalchemy`)
- **Visuals**: Plotly & Altair (Python-based charting)

## Features
- **Fleet Dashboard**: Basic fleet status monitoring.
- **Insights**: Static analysis views.
- **User Management**: Admin tools for user CRUD.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r streamlit/requirements.txt
    ```

2.  **Run the App**:
    Run this command from the **project root** directory:
    ```bash
    streamlit run streamlit/main.py
    ```

3.  **Access**:
    Open the URL displayed in the terminal (usually [http://localhost:8501](http://localhost:8501)).
