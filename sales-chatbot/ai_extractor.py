"""
AI Parameter Extractor - Use Gemini to extract query parameters
Simple, clean, and reliable
"""

import json
import os
import time
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def extract_parameters(question: str, retry_count: int = 3) -> dict:
    """
    Use Gemini to extract query parameters from natural language
    
    Args:
        question: User's natural language question
        retry_count: Number of retries on failure
        
    Returns:
        dict: Extracted parameters
            {
                "brand": str or None,
                "product": str or None,
                "month": str or None,
                "year": int or None,
                "region": str or None,
                "metric": "sales" or "active_stores",
                "aggregation": "sum" or "count" or "average",
                "comparison": "yoy" or None,
                "top_n": int or None
            }
    """
    
    prompt = f"""Extract parameters from this sales data question and return ONLY valid JSON.

Question: "{question}"

Return JSON with these exact fields:
- brand: brand name or null (e.g., "Lays", "Coke", "Neo", "Delmond")
- product: product/category name or null (e.g., "Biscuits", "Cheese", "Chocolate", "CEREALS")
- month: month name or null (e.g., "January", "JAN", "Feb")
- year: year number or null (e.g., 2024, 2025)
- region: region/area name or null
- metric: "sales" or "active_stores" (default: "sales")
- aggregation: "sum" or "count" or "average" (default: "sum")
- comparison: "yoy" (year-over-year) or null
- top_n: number for "top N" queries or null (e.g., "top 5 brands" → 5)

Examples:

Question: "What were Lays sales in January 2024?"
Output: {{"brand": "Lays", "product": null, "month": "January", "year": 2024, "region": null, "metric": "sales", "aggregation": "sum", "comparison": null, "top_n": null}}

Question: "Compare sales between 2023 and 2024"
Output: {{"brand": null, "product": null, "month": null, "year": 2024, "region": null, "metric": "sales", "aggregation": "sum", "comparison": "yoy", "top_n": null}}

Question: "Show me top 5 brands by sales"
Output: {{"brand": null, "product": null, "month": null, "year": null, "region": null, "metric": "sales", "aggregation": "sum", "comparison": null, "top_n": 5}}

Question: "How many active stores did Coke have in Q1 2024?"
Output: {{"brand": "Coke", "product": null, "month": null, "year": 2024, "region": null, "metric": "active_stores", "aggregation": "count", "comparison": null, "top_n": null}}

Question: "What were total sales of Biscuits in 2024?"
Output: {{"brand": null, "product": "Biscuits", "month": null, "year": 2024, "region": null, "metric": "sales", "aggregation": "sum", "comparison": null, "top_n": null}}

Return ONLY the JSON object, no other text.
"""
    
    for attempt in range(retry_count):
        try:
            # Use Gemini Flash Lite Latest (free with higher limits)
            model_name = 'gemini-flash-lite-latest'
            model = genai.GenerativeModel(model_name)
            print(f"DEBUG - Using model: {model_name}")
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Debug: Print raw response
            print(f"DEBUG - Gemini raw response: {response_text[:200]}")
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse JSON
            params = json.loads(response_text)
            
            # Debug: Print parsed params
            print(f"DEBUG - Parsed params: {params}")
            
            # Validate and set defaults
            params = validate_parameters(params)
            
            return params
            
        except json.JSONDecodeError as e:
            print(f"DEBUG - JSON decode error: {e}")
            print(f"DEBUG - Response text was: {response_text}")
            if attempt < retry_count - 1:
                time.sleep(1)  # Wait before retry
                continue
            else:
                # Return default parameters on failure
                print("DEBUG - Returning default parameters due to JSON error")
                return get_default_parameters()
                
        except Exception as e:
            print(f"DEBUG - Exception in extract_parameters: {type(e).__name__}: {e}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                # Return default parameters on failure
                print("DEBUG - Returning default parameters due to exception")
                return get_default_parameters()
    
    return get_default_parameters()


def validate_parameters(params: dict) -> dict:
    """
    Validate and normalize extracted parameters
    
    Args:
        params: Raw parameters from AI
        
    Returns:
        dict: Validated parameters with defaults
    """
    validated = {
        'brand': params.get('brand'),
        'product': params.get('product'),
        'month': params.get('month'),
        'year': params.get('year'),
        'region': params.get('region'),
        'metric': params.get('metric', 'sales'),
        'aggregation': params.get('aggregation', 'sum'),
        'comparison': params.get('comparison'),
        'top_n': params.get('top_n'),
    }
    
    # Ensure metric is valid
    if validated['metric'] not in ['sales', 'active_stores']:
        validated['metric'] = 'sales'
    
    # Ensure aggregation is valid
    if validated['aggregation'] not in ['sum', 'count', 'average']:
        validated['aggregation'] = 'sum'
    
    # Convert year to int if present
    if validated['year']:
        try:
            validated['year'] = int(validated['year'])
        except:
            validated['year'] = None
    
    # Convert top_n to int if present
    if validated['top_n']:
        try:
            validated['top_n'] = int(validated['top_n'])
        except:
            validated['top_n'] = None
    
    return validated


def get_default_parameters() -> dict:
    """
    Return default parameters when extraction fails
    
    Returns:
        dict: Default parameters
    """
    return {
        'brand': None,
        'product': None,
        'month': None,
        'year': None,
        'region': None,
        'metric': 'sales',
        'aggregation': 'sum',
        'comparison': None,
        'top_n': None,
    }
