# Marine-Web (HTMX Version)

This is the **Next-Gen** version of the MarineOS Dashboard, built for high performance and premium UX using **FastAPI** + **HTMX** + **TailwindCSS**.

## Architecture
- **Backend**: FastAPI (Async Python)
- **Frontend**: HTMX (Hypermedia-driven interactions)
- **Styling**: Tailwind CSS (via CDN for prototyping)
- **Database**: PostgreSQL (via `psycopg2` & `sqlalchemy`)

## Features
- **Real-time Fleet Monitoring**: Live stats and interactive map (Leaflet.js).
- **Analytics**: Revenue and utilization charts (Chart.js) with lazy loading.
- **System Logs**: Audit trail and client management with efficient pagination.
- **Zero-Build**: No complex frontend build step required (Templates + CDN).

## Project Structure
- `main.py`: Application entry point.
- `routes/`: Endpoint logic (`dashboard`, `analytics`, `tables`).
- `core/`: Database logic (pure python).
- `templates/`: Jinja2 HTML templates.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r htmx/requirements.txt
    ```

2.  **Run the Server**:
    Run this command from the **project root** directory:
    ```bash
    python -m uvicorn htmx.main:app --reload
    ```

3.  **Access**:
    Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
