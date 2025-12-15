"""
Data Loader - Load and cache Excel data
Simple, clean, and efficient
"""

import pandas as pd
import streamlit as st

# Month name mapping for normalization
MONTH_MAPPING = {
    'january': 'JAN', 'jan': 'JAN',
    'february': 'FEB', 'feb': 'FEB',
    'march': 'MAR', 'mar': 'MAR',
    'april': 'APR', 'apr': 'APR',
    'may': 'MAY',
    'june': 'JUN', 'jun': 'JUN',
    'july': 'JUL', 'jul': 'JUL',
    'august': 'AUG', 'aug': 'AUG',
    'september': 'SEP', 'sep': 'SEP',
    'october': 'OCT', 'oct': 'OCT',
    'november': 'NOV', 'nov': 'NOV',
    'december': 'DEC', 'dec': 'DEC',
}


def normalize_month(month_str: str) -> str:
    """
    Normalize month name to 3-letter uppercase format
    
    Args:
        month_str: Month name (e.g., "January", "jan", "JAN")
        
    Returns:
        str: Normalized month (e.g., "JAN")
    """
    if not month_str:
        return None
    
    month_lower = str(month_str).strip().lower()
    return MONTH_MAPPING.get(month_lower, month_str.upper())


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load Excel file into Pandas DataFrame
    Cached so it only runs once per session
    
    Why we use "Sales 2022 Onwards" sheet:
    - "Sales" sheet: Pivot table (not raw data)
    - "Active Store" sheet: Pivot table (not raw data)
    - "Sales 2022 Onwards": Raw transactional data (22,762 rows) ✅
    
    We calculate active stores dynamically from raw data for flexibility.
    
    Returns:
        pd.DataFrame: Cleaned sales data from "Sales 2022 Onwards" sheet
    """
    try:
        # Load the main sales sheet (raw transactional data)
        df = pd.read_excel(
            'data/Sales & Active Stores Data.xlsb',
            sheet_name='Sales 2022 Onwards',
            engine='pyxlsb'
        )
        
        # Clean column names (lowercase, remove spaces)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Ensure proper data types
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            # Create 'sales' alias for easier querying
            df['sales'] = df['value']
        
        if 'customer_account_number' in df.columns:
            # Create 'store_id' alias for active stores counting
            df['store_id'] = df['customer_account_number']
        
        if 'month' in df.columns:
            # Normalize months to 3-letter uppercase (JAN, FEB, etc.)
            df['month'] = df['month'].apply(normalize_month)
        
        # Validate required columns exist
        required_columns = ['brand', 'year', 'month', 'value']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"❌ Missing required columns: {missing}")
            return pd.DataFrame()
        
        return df
        
    except FileNotFoundError:
        st.error("❌ Excel file not found. Make sure 'Sales & Active Stores Data.xlsb' is in the data/ folder")
        return pd.DataFrame()
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()


def get_data_info(df: pd.DataFrame) -> dict:
    """
    Get summary information about the dataset
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Summary statistics
    """
    if df.empty:
        return {}
    
    return {
        'total_rows': len(df),
        'columns': len(df.columns),
        'date_range': f"{df['year'].min()} - {df['year'].max()}" if 'year' in df.columns else 'N/A',
        'total_sales': f"₹{df['sales'].sum():,.2f}" if 'sales' in df.columns else 'N/A',
        'brands': df['brand'].nunique() if 'brand' in df.columns else 'N/A',
        'unique_stores': df['store_id'].nunique() if 'store_id' in df.columns else 'N/A',
    }
