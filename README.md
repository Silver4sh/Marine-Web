# Marine Analytics Dashboard 🚢

A comprehensive marine fleet management and environmental monitoring dashboard built with [Streamlit](https://streamlit.io/). This application provides real-time insights into vessel operations, financial metrics, and environmental data analysis.

## ✨ Key Features

- **Interactive Dashboard**: Real-time KPIs for fleet status, orders, and financial performance.
- **Role-Based Access Control**: Tailored views for Admin, Operations, Marcom, and Finance roles.
- **Vessel Map**: Visualize vessel locations and status on an interactive map.
- **Environmental Heatmap**: Monitor water quality (Salinity, Turbidity, Oxygen) and oceanographic data (Current, Tide, Density).
- **Historical Data**: Analyze sensor data trends over time.
- **Client Management**: Overview of client portfolio and active regions.

## 🛠️ Technology Stack

- **Frontend/Backend**: Python, Streamlit
- **Data Manipulation**: Pandas, NumPy
- **Visualization**: Plotly, Altair, Folium
- **Database**: PostgreSQL (via SQLAlchemy & Psycopg2)

## 📂 Project Structure

```
Marine-Web/
├── dashboard/
│   ├── main.py              # Application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── back/                # Backend logic
│   │   ├── conection/       # Database & Login connections
│   │   ├── query/           # SQL queries
│   │   └── src/             # Page logic (Map, Heatmap, History)
│   └── front/               # Frontend assets (CSS, HTML)
├── database/
│   └── table.sql            # Database schema
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Marine-Web.git
   cd Marine-Web
   ```

2. **Install dependencies**
   ```bash
   pip install -r dashboard/requirements.txt
   ```

3. **Configure Environment**
   - Ensure you have a `.env` file or environment variables set up for database connection.
   
4. **Run the Application**
   ```bash
   streamlit run dashboard/main.py
   ```

## 📝 Usage

1. Open your browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).
2. Log in using your credentials.
3. Navigate through the sidebar menu to access different modules.
