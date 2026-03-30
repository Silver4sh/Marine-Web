"""core/services/report.py — Auto-generation tool for Executive Reports"""
import pandas as pd
import io
from typing import Dict

def generate_excel_report(dfs: Dict[str, pd.DataFrame]) -> bytes:
    """
    Generate an Excel file with multiple sheets from a dictionary of DataFrames.
    Optimized for memory usage and string conversion.
    """
    output = io.BytesIO()
    # Optimize writer using in_memory string caching and conversion
    with pd.ExcelWriter(
        output,
        engine='xlsxwriter',
        engine_kwargs={'options': {'in_memory': True, 'strings_to_numbers': True}}
    ) as writer:
        for sheet_name, df in dfs.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Create an empty sheet with a message efficiently
                empty_df = pd.DataFrame([{"Message": f"No data available for {sheet_name}"}])
                empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output.getvalue()
