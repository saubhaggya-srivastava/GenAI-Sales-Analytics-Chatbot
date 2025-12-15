"""
Utility functions - Export, error handling, examples
Simple and clean
"""

import pandas as pd
from datetime import datetime
import traceback


def export_to_csv(df: pd.DataFrame, query: str = "") -> str:
    """
    Convert DataFrame to CSV string
    
    Args:
        df: DataFrame to export
        query: Original query (for metadata)
        
    Returns:
        str: CSV data
    """
    return df.to_csv(index=False)


def generate_filename(query: str = "") -> str:
    """
    Generate filename for CSV export
    
    Args:
        query: User's query
        
    Returns:
        str: Filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean query for filename
    clean_query = "".join(c for c in query[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_query = clean_query.replace(' ', '_')
    
    if clean_query:
        return f"sales_data_{clean_query}_{timestamp}.csv"
    else:
        return f"sales_data_{timestamp}.csv"


def handle_error(error: Exception, context: str = "") -> dict:
    """
    Handle errors and return user-friendly messages
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        
    Returns:
        dict: Error information
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # User-friendly messages
    if "API" in error_msg or "api" in error_msg:
        message = "AI service is temporarily unavailable"
        suggestion = "Please try again in a moment"
    elif "KeyError" in error_type:
        message = "Data column not found"
        suggestion = "Try rephrasing your question"
    elif "ValueError" in error_type:
        message = "Invalid data in your query"
        suggestion = "Check your brand names, dates, or numbers"
    else:
        message = "Something went wrong"
        suggestion = "Try asking: 'What were total sales in 2024?'"
    
    return {
        'message': message,
        'suggestion': suggestion,
        'technical': f"{error_type}: {error_msg}\n\n{traceback.format_exc()}"
    }


def get_example_queries() -> list:
    """
    Get example queries organized by category
    
    Returns:
        list: Example queries by category
    """
    return [
        {
            'category': '💰 Sales Queries',
            'queries': [
                "What were total sales for Lays in January 2024?",
                "Show me sales for Neo in 2024",
                "Total sales in February 2025",
            ]
        },
        {
            'category': '🏪 Active Stores',
            'queries': [
                "How many active stores did Delphy have in 2024?",
                "Active stores for Coke in January 2024",
                "Show me store count for Titz",
            ]
        },
        {
            'category': '📈 Comparisons',
            'queries': [
                "Compare sales between 2024 and 2025",
                "Year over year sales growth",
                "Show me YoY comparison for Solerone",
            ]
        },
        {
            'category': '🏆 Rankings',
            'queries': [
                "Show me top 5 brands by sales",
                "Top 3 brands by active stores",
                "Which brands have the highest sales?",
            ]
        },
    ]
