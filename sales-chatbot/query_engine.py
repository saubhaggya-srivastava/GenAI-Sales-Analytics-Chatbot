"""
Pandas Query Engine - Filter and aggregate data
Simple, clean, and powerful
"""

import pandas as pd
from typing import Union, Optional
from data_loader import normalize_month


def query_data(df: pd.DataFrame, params: dict) -> Union[pd.DataFrame, float, int, dict]:
    """
    Filter and aggregate DataFrame based on extracted parameters
    Pure Python/Pandas - YOU control the logic
    
    Args:
        df: Sales DataFrame
        params: Extracted parameters from AI
        
    Returns:
        Union[pd.DataFrame, float, int, dict]: Query results
    """
    if df.empty:
        return {"error": "No data available"}
    
    # Start with full dataset
    result = df.copy()
    
    # Apply filters
    if params.get('brand'):
        result = result[result['brand'].str.lower() == params['brand'].lower()]
    
    if params.get('product'):
        # Check if 'category' column exists (for product categories like Biscuits, Cheese)
        if 'category' in result.columns:
            result = result[result['category'].str.lower() == params['product'].lower()]
        # Fallback to sub_brand if it exists
        elif 'sub_brand' in result.columns:
            result = result[result['sub_brand'].str.lower() == params['product'].lower()]
    
    if params.get('month'):
        # Normalize month to match data format (JAN, FEB, etc.)
        normalized_month = normalize_month(params['month'])
        result = result[result['month'] == normalized_month]
    
    # Don't filter by year if doing YoY comparison (we need multiple years!)
    if params.get('year') and not params.get('comparison') == 'yoy':
        result = result[result['year'] == params['year']]
    
    if params.get('region'):
        # Check both 'area' and 'city' columns
        region_lower = params['region'].lower()
        result = result[
            (result['area'].str.lower() == region_lower) |
            (result['city'].str.lower() == region_lower)
        ]
    
    # Check if we have results after filtering
    if result.empty:
        return {
            "error": "No data found",
            "message": "No results match your filters. Try different criteria.",
            "filters_applied": {k: v for k, v in params.items() if v is not None}
        }
    
    # Handle special query types
    if params.get('top_n'):
        return get_top_n(result, params)
    
    if params.get('comparison') == 'yoy':
        return calculate_yoy(result, params)
    
    # Standard aggregation
    metric = params.get('metric', 'sales')
    aggregation = params.get('aggregation', 'sum')
    
    if metric == 'sales':
        if aggregation == 'sum':
            total = result['sales'].sum()
            return {
                'value': total,
                'formatted': f"₹{total:,.2f}",
                'row_count': len(result),
                'data': result[['brand', 'month', 'year', 'sales']].head(100)
            }
        elif aggregation == 'average':
            avg = result['sales'].mean()
            return {
                'value': avg,
                'formatted': f"₹{avg:,.2f}",
                'row_count': len(result),
                'data': result[['brand', 'month', 'year', 'sales']].head(100)
            }
    
    elif metric == 'active_stores':
        # Active stores = stores with NET SALES > 0 (excludes returns that cancel out sales)
        store_net_sales = result.groupby('store_id')['sales'].sum()
        active_stores_with_positive_sales = store_net_sales[store_net_sales > 0]
        count = len(active_stores_with_positive_sales)
        
        # Get store IDs with positive net sales for display
        active_store_ids = active_stores_with_positive_sales.index.tolist()
        display_data = result[result['store_id'].isin(active_store_ids)][['brand', 'month', 'year', 'store_id']].drop_duplicates('store_id').head(100)
        
        return {
            'value': count,
            'formatted': f"{count:,} stores",
            'row_count': len(result),
            'data': display_data
        }
    
    # Default: return filtered data
    return {
        'value': len(result),
        'formatted': f"{len(result):,} records",
        'row_count': len(result),
        'data': result.head(100)
    }


def get_top_n(df: pd.DataFrame, params: dict) -> dict:
    """
    Get top N items by metric
    
    Args:
        df: Filtered DataFrame
        params: Query parameters
        
    Returns:
        dict: Top N results with data
    """
    n = params.get('top_n', 5)
    metric = params.get('metric', 'sales')
    
    if metric == 'sales':
        # Group by brand and sum sales
        grouped = df.groupby('brand')['sales'].sum().nlargest(n).reset_index()
        grouped['percentage'] = (grouped['sales'] / grouped['sales'].sum() * 100).round(2)
        
        return {
            'value': n,
            'formatted': f"Top {n} brands by sales",
            'row_count': len(grouped),
            'data': grouped,
            'chart_type': 'bar'
        }
    
    elif metric == 'active_stores':
        # Active stores = stores with NET SALES > 0 per brand
        # Group by brand and store, sum sales, then count stores with positive sales
        brand_store_sales = df.groupby(['brand', 'store_id'])['sales'].sum().reset_index()
        
        # Count stores with positive net sales per brand
        active_by_brand = (
            brand_store_sales[brand_store_sales['sales'] > 0]
            .groupby('brand')['store_id']
            .nunique()
            .nlargest(n)
            .reset_index()
        )
        active_by_brand.columns = ['brand', 'active_stores']
        active_by_brand['percentage'] = (active_by_brand['active_stores'] / active_by_brand['active_stores'].sum() * 100).round(2)
        
        return {
            'value': n,
            'formatted': f"Top {n} brands by active stores",
            'row_count': len(active_by_brand),
            'data': active_by_brand,
            'chart_type': 'bar'
        }
    
    return {"error": "Invalid metric for top N query"}


def calculate_yoy(df: pd.DataFrame, params: dict) -> dict:
    """
    Calculate year-over-year comparison
    
    Args:
        df: Filtered DataFrame
        params: Query parameters
        
    Returns:
        dict: YoY comparison results
    """
    metric = params.get('metric', 'sales')
    
    if metric == 'sales':
        # Group by year and sum sales
        yearly = df.groupby('year')['sales'].sum().reset_index()
        yearly = yearly.sort_values('year')
        
        # Calculate YoY change
        if len(yearly) >= 2:
            yearly['yoy_change_pct'] = yearly['sales'].pct_change() * 100
            yearly['yoy_change_abs'] = yearly['sales'].diff()
            
            return {
                'value': len(yearly),
                'formatted': f"Year-over-year sales comparison ({len(yearly)} years)",
                'row_count': len(yearly),
                'data': yearly,
                'chart_type': 'line'
            }
        else:
            return {
                'error': 'Insufficient data',
                'message': 'Need at least 2 years of data for YoY comparison',
                'data': yearly
            }
    
    elif metric == 'active_stores':
        # Active stores = stores with NET SALES > 0 per year
        # Group by year and store, sum sales, then count stores with positive sales
        yearly_store_sales = df.groupby(['year', 'store_id'])['sales'].sum().reset_index()
        
        # Count stores with positive net sales per year
        active_by_year = (
            yearly_store_sales[yearly_store_sales['sales'] > 0]
            .groupby('year')['store_id']
            .nunique()
            .reset_index()
        )
        active_by_year.columns = ['year', 'active_stores']
        active_by_year = active_by_year.sort_values('year')
        
        # Calculate YoY change
        if len(active_by_year) >= 2:
            active_by_year['yoy_change_pct'] = active_by_year['active_stores'].pct_change() * 100
            active_by_year['yoy_change_abs'] = active_by_year['active_stores'].diff()
            
            return {
                'value': len(active_by_year),
                'formatted': f"Year-over-year active stores comparison ({len(active_by_year)} years)",
                'row_count': len(active_by_year),
                'data': active_by_year,
                'chart_type': 'line'
            }
        else:
            return {
                'error': 'Insufficient data',
                'message': 'Need at least 2 years of data for YoY comparison',
                'data': active_by_year
            }
    
    return {"error": "Invalid metric for YoY comparison"}


def format_result_message(result: dict, params: dict) -> str:
    """
    Generate natural language message for results
    
    Args:
        result: Query result
        params: Query parameters
        
    Returns:
        str: Natural language message
    """
    if 'error' in result:
        return f"❌ {result.get('message', result['error'])}"
    
    # Build context from parameters
    context_parts = []
    if params.get('brand'):
        context_parts.append(f"for {params['brand']}")
    if params.get('month'):
        context_parts.append(f"in {params['month']}")
    if params.get('year'):
        context_parts.append(f"{params['year']}")
    if params.get('region'):
        context_parts.append(f"in {params['region']}")
    
    context = " ".join(context_parts)
    
    # Format message based on query type
    if params.get('top_n'):
        return f"📊 {result['formatted']}"
    elif params.get('comparison') == 'yoy':
        return f"📈 {result['formatted']}"
    elif params.get('metric') == 'active_stores':
        return f"🏪 **{result['formatted']}** {context}"
    else:
        return f"💰 **{result['formatted']}** {context}"
