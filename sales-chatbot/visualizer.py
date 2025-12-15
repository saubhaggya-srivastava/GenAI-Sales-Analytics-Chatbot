"""
Visualizer - Create charts with Plotly
Simple and clean
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_chart(data: pd.DataFrame, params: dict, result: dict):
    """
    Create appropriate chart based on data and query type
    
    Args:
        data: DataFrame to visualize
        params: Query parameters
        result: Query result dict
        
    Returns:
        plotly figure or None
    """
    if data.empty or len(data) == 0:
        return None
    
    chart_type = result.get('chart_type', 'auto')
    
    try:
        # Top N rankings - Bar chart
        if params.get('top_n') or chart_type == 'bar':
            if 'brand' in data.columns and 'sales' in data.columns:
                fig = px.bar(
                    data,
                    x='brand',
                    y='sales',
                    title=f"Top {params.get('top_n', len(data))} Brands by Sales",
                    labels={'sales': 'Sales (₹)', 'brand': 'Brand'},
                    text='sales'
                )
                fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                return fig
            elif 'brand' in data.columns and 'active_stores' in data.columns:
                fig = px.bar(
                    data,
                    x='brand',
                    y='active_stores',
                    title=f"Top {params.get('top_n', len(data))} Brands by Active Stores",
                    labels={'active_stores': 'Active Stores', 'brand': 'Brand'},
                    text='active_stores'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                return fig
        
        # Year-over-year - Line chart
        if params.get('comparison') == 'yoy' or chart_type == 'line':
            if 'year' in data.columns and 'sales' in data.columns:
                fig = px.line(
                    data,
                    x='year',
                    y='sales',
                    title="Year-over-Year Sales Comparison",
                    labels={'sales': 'Sales (₹)', 'year': 'Year'},
                    markers=True
                )
                fig.update_traces(line=dict(width=3))
                return fig
            elif 'year' in data.columns and 'active_stores' in data.columns:
                fig = px.line(
                    data,
                    x='year',
                    y='active_stores',
                    title="Year-over-Year Active Stores Comparison",
                    labels={'active_stores': 'Active Stores', 'year': 'Year'},
                    markers=True
                )
                fig.update_traces(line=dict(width=3))
                return fig
        
        # Default: return None (no chart)
        return None
        
    except Exception as e:
        print(f"Chart creation error: {e}")
        return None


def format_dataframe_for_display(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Format DataFrame for nice display in Streamlit
    
    Args:
        df: DataFrame to format
        params: Query parameters
        
    Returns:
        Formatted DataFrame
    """
    if df.empty:
        return df
    
    # Make a copy
    display_df = df.copy()
    
    # Format sales columns
    if 'sales' in display_df.columns:
        display_df['sales'] = display_df['sales'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "")
    
    # Format percentage columns
    if 'percentage' in display_df.columns:
        display_df['percentage'] = display_df['percentage'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    
    if 'yoy_change_pct' in display_df.columns:
        display_df['yoy_change_pct'] = display_df['yoy_change_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "")
    
    if 'yoy_change_abs' in display_df.columns:
        display_df['yoy_change_abs'] = display_df['yoy_change_abs'].apply(lambda x: f"₹{x:+,.2f}" if pd.notna(x) else "")
    
    # Capitalize column names
    display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]
    
    return display_df
