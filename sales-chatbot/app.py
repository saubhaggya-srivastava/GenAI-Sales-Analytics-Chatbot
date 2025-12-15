# Sales Data Analysis Chatbot
# Simple Pandas-based approach - No database needed!

import streamlit as st
import pandas as pd
from data_loader import load_data, get_data_info
from ai_extractor import extract_parameters
from query_engine import query_data, format_result_message
from visualizer import create_chart, format_dataframe_for_display
from utils import export_to_csv, generate_filename, handle_error, get_example_queries


def main():
    st.set_page_config(
        page_title="Sales Data Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Sales Data Analysis Chatbot")
    st.markdown("Ask questions about sales data in natural language!")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Example Queries")
        
        examples = get_example_queries()
        for category_data in examples:
            with st.expander(category_data['category']):
                for query in category_data['queries']:
                    if st.button(query, key=query, use_container_width=True):
                        # Add query to chat
                        st.session_state.messages.append({"role": "user", "content": query})
                        st.rerun()
        
        st.divider()
        
        # Data info
        if st.session_state.data_loaded:
            st.subheader("📊 Dataset Info")
            try:
                df = load_data()
                info = get_data_info(df)
                st.metric("Total Records", f"{info.get('total_rows', 0):,}")
                st.metric("Date Range", info.get('date_range', 'N/A'))
                st.metric("Total Sales", info.get('total_sales', 'N/A'))
                st.metric("Unique Brands", info.get('brands', 'N/A'))
                st.metric("Unique Stores", info.get('unique_stores', 'N/A'))
            except:
                pass
        
        st.divider()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.data_loaded = False
            st.success("Data refreshed!")
            st.rerun()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Load data
    try:
        with st.spinner("Loading data..."):
            df = load_data()
            st.session_state.data_loaded = True
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display data and chart if available
            if message["role"] == "assistant" and "data" in message:
                if message.get("chart"):
                    st.plotly_chart(message["chart"], use_container_width=True)
                
                if message.get("show_data"):
                    with st.expander("📋 View Data"):
                        st.dataframe(message["data"], use_container_width=True)
                        
                        # Export button with unique key
                        if message["data"] is not None and not message["data"].empty:
                            csv_data = export_to_csv(message["data"], message.get("query", ""))
                            filename = generate_filename(message.get("query", ""))
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=filename,
                                mime="text/csv",
                                key=f"download_btn_{idx}"  # Unique key for each button
                            )
    
    # Check if we need to process a pending query (from sidebar button)
    needs_processing = (
        len(st.session_state.messages) > 0 and 
        st.session_state.messages[-1]["role"] == "user" and
        (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant")
    )
    
    # Chat input
    if prompt := st.chat_input("Ask about sales data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        needs_processing = True
    
    # Process query if needed
    if needs_processing:
        prompt = st.session_state.messages[-1]["content"]

        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Extract parameters
                    params = extract_parameters(prompt)
                    
                    # Debug: Show extracted parameters
                    with st.expander("🔍 Debug: Extracted Parameters"):
                        st.json(params)
                    
                    # Query data
                    result = query_data(df, params)
                    
                    # Format message
                    message = format_result_message(result, params)
                    st.markdown(message)
                    
                    # Create chart if applicable
                    chart = None
                    if 'data' in result and isinstance(result['data'], pd.DataFrame) and not result['data'].empty:
                        chart = create_chart(result['data'], params, result)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                    
                    # Show data table
                    if 'data' in result and isinstance(result['data'], pd.DataFrame) and not result['data'].empty:
                        formatted_data = format_dataframe_for_display(result['data'], params)
                        
                        with st.expander("📋 View Data"):
                            st.dataframe(formatted_data, use_container_width=True)
                            
                            # Export button with unique key
                            csv_data = export_to_csv(result['data'], prompt)
                            filename = generate_filename(prompt)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=filename,
                                mime="text/csv",
                                key=f"download_btn_new_{len(st.session_state.messages)}"  # Unique key
                            )
                    
                    # Save assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": message,
                        "data": formatted_data if 'data' in result else None,
                        "chart": chart,
                        "show_data": True,
                        "query": prompt
                    })
                    
                except Exception as e:
                    error_info = handle_error(e, "query processing")
                    st.error(f"❌ {error_info['message']}")
                    st.info(f"💡 {error_info['suggestion']}")
                    
                    with st.expander("🔍 Technical Details"):
                        st.code(error_info['technical'])
                    
                    # Save error message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ {error_info['message']}\n\n💡 {error_info['suggestion']}"
                    })


if __name__ == "__main__":
    main()
