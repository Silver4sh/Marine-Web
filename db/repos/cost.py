"""db/repos/cost.py — Repo untuk data biaya operasional voyage"""
import pandas as pd
from typing import Dict, List, Any

def get_voyage_costs() -> pd.DataFrame:
    """Mock operational cost data for dredging vessels."""
    data: List[Dict[str, Any]] = [
        {"vessel_name": "TSHD Barito", "fuel_cost": 150000000, "crew_cost": 45000000, "maintenance_cost": 20000000, "month": "Jan"},
        {"vessel_name": "TSHD Barito", "fuel_cost": 155000000, "crew_cost": 45000000, "maintenance_cost": 25000000, "month": "Feb"},
        {"vessel_name": "CSD Musi", "fuel_cost": 120000000, "crew_cost": 40000000, "maintenance_cost": 15000000, "month": "Jan"},
        {"vessel_name": "CSD Musi", "fuel_cost": 125000000, "crew_cost": 40000000, "maintenance_cost": 18000000, "month": "Feb"},
    ]
    return pd.DataFrame(data)
