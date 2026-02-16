import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Call Analysis Dashboard",
    page_icon="📞",
    layout="wide"
)

# Title
st.title("📞 Call Analysis Dashboard")

# Load data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    # Convert duration to numeric if needed
    df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(0)
    # Parse time
    df['Time'] = pd.to_datetime(df['Time'])
    return df

# File uploader
uploaded_file = st.file_uploader("Upload your call data CSV", type=['csv'])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    st.success(f"✅ Loaded {len(df):,} call records")
    
    # Sidebar for filters
    st.sidebar.header("🔍 Filters")
    
    # Use Case filter
    use_cases = sorted(df['Use Case'].unique())
    selected_use_cases = st.sidebar.multiselect(
        "Select Use Cases",
        options=use_cases,
        default=use_cases,
        help="Filter by use case"
    )
    
    # Call Status filter
    call_statuses = sorted(df['Call Status'].unique())
    selected_statuses = st.sidebar.multiselect(
        "Select Call Status",
        options=call_statuses,
        default=call_statuses,
        help="Filter by call status"
    )
    
    # Task Completion filter
    task_completions = sorted(df['Analysis.task_completion'].unique())
    selected_completions = st.sidebar.multiselect(
        "Select Task Completion",
        options=task_completions,
        default=task_completions,
        help="Filter by task completion status"
    )
    
    # Duration filter
    st.sidebar.subheader("Duration Range (seconds)")
    min_duration = int(df['Duration'].min())
    max_duration = int(df['Duration'].max())
    
    duration_range = st.sidebar.slider(
        "Select duration range",
        min_value=min_duration,
        max_value=max_duration,
        value=(min_duration, max_duration),
        help="Filter by call duration in seconds"
    )
    
    # Number exclusion
    st.sidebar.subheader("🚫 Exclude Numbers")
    exclude_numbers = st.sidebar.text_area(
        "Enter numbers to exclude (one per line)",
        height=100,
        help="Add phone numbers to exclude from analysis"
    )
    
    # Parse excluded numbers
    excluded_numbers_list = []
    if exclude_numbers:
        excluded_numbers_list = [num.strip() for num in exclude_numbers.split('\n') if num.strip()]
    
    # Apply filters
    filtered_df = df[
        (df['Use Case'].isin(selected_use_cases)) &
        (df['Call Status'].isin(selected_statuses)) &
        (df['Analysis.task_completion'].isin(selected_completions)) &
        (df['Duration'] >= duration_range[0]) &
        (df['Duration'] <= duration_range[1])
    ]
    
    # Apply number exclusion
    if excluded_numbers_list:
        filtered_df = filtered_df[~filtered_df['Number'].isin(excluded_numbers_list)]
        st.sidebar.info(f"Excluding {len(excluded_numbers_list)} numbers")
    
    # Display filter summary
    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Records", f"{len(filtered_df):,}")
    st.sidebar.metric("Excluded", f"{len(df) - len(filtered_df):,}")
    
    # Main metrics
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_calls = len(filtered_df)
    call_placed = len(filtered_df[filtered_df['Call Status'] == 'call_placed'])
    could_not_connect = len(filtered_df[filtered_df['Call Status'] == 'could_not_connect'])
    completed = len(filtered_df[filtered_df['Call Status'] == 'completed'])
    
    # Task completion success (true only)
    task_success = len(filtered_df[filtered_df['Analysis.task_completion'] == 'true'])
    
    # Average duration (only for completed calls)
    avg_duration = filtered_df[filtered_df['Duration'] > 0]['Duration'].mean()
    
    with col1:
        st.metric("Calls Made", f"{total_calls:,}")
    with col2:
        st.metric("Call Placed", f"{call_placed:,}")
    with col3:
        st.metric("Could Not Connect", f"{could_not_connect:,}")
    with col4:
        st.metric("Call Completed", f"{completed:,}")
    with col5:
        st.metric("Call Success", f"{task_success:,}")
        if completed > 0:
            success_rate = (task_success / completed) * 100
            st.caption(f"{success_rate:.1f}% of completed")
    with col6:
        st.metric("Avg Duration", f"{avg_duration:.1f}s" if not pd.isna(avg_duration) else "N/A")
    
    # Table selector
    st.header("📋 Analysis Tables")
    st.markdown("Select which tables to display:")
    
    table_options = {
        "Summary by Use Case": "use_case_summary",
        "Summary by Call Status": "call_status_summary",
        "Summary by Task Completion": "task_completion_summary",
        "Duration Analysis": "duration_analysis",
        "Hourly Analysis": "hourly_analysis",
        "Daily Analysis": "daily_analysis",
        "Recent Calls Detail": "recent_calls"
    }
    
    selected_tables = st.multiselect(
        "Choose tables to display (select 3-5)",
        options=list(table_options.keys()),
        default=list(table_options.keys())[:5],
        max_selections=5
    )
    
    # Display tables
    if selected_tables:
        # Create columns for side-by-side display
        if len(selected_tables) <= 2:
            cols = st.columns(len(selected_tables))
        else:
            # For 3+ tables, display in rows of 2
            num_rows = (len(selected_tables) + 1) // 2
            
        table_idx = 0
        for i in range(0, len(selected_tables), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(selected_tables):
                    table_name = selected_tables[i + j]
                    table_key = table_options[table_name]
                    
                    with col:
                        st.subheader(table_name)
                        
                        # Generate table based on selection
                        if table_key == "use_case_summary":
                            summary = filtered_df.groupby('Use Case').agg({
                                'Number': 'count',
                                'Call Status': lambda x: (x == 'completed').sum(),
                                'Duration': 'mean',
                                'Analysis.task_completion': lambda x: (x == 'true').sum()
                            }).round(1)
                            summary.columns = ['Total Calls', 'Completed', 'Avg Duration (s)', 'Success']
                            summary['Success Rate %'] = ((summary['Success'] / summary['Completed']) * 100).round(1)
                            summary = summary.fillna(0)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "call_status_summary":
                            summary = filtered_df.groupby('Call Status').agg({
                                'Number': 'count',
                                'Duration': ['mean', 'max', 'sum']
                            }).round(1)
                            summary.columns = ['Count', 'Avg Duration (s)', 'Max Duration (s)', 'Total Duration (s)']
                            summary['Percentage'] = ((summary['Count'] / summary['Count'].sum()) * 100).round(1)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "task_completion_summary":
                            summary = filtered_df.groupby('Analysis.task_completion').agg({
                                'Number': 'count',
                                'Duration': 'mean',
                                'Call Status': lambda x: (x == 'completed').sum()
                            }).round(1)
                            summary.columns = ['Count', 'Avg Duration (s)', 'Completed Calls']
                            summary['Percentage'] = ((summary['Count'] / summary['Count'].sum()) * 100).round(1)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "duration_analysis":
                            # Create duration buckets
                            bins = [0, 10, 30, 60, 120, 300, float('inf')]
                            labels = ['0-10s', '11-30s', '31-60s', '1-2min', '2-5min', '5min+']
                            filtered_df['Duration_Bucket'] = pd.cut(filtered_df['Duration'], bins=bins, labels=labels, include_lowest=True)
                            
                            summary = filtered_df.groupby('Duration_Bucket', observed=True).agg({
                                'Number': 'count',
                                'Analysis.task_completion': lambda x: (x == 'true').sum()
                            })
                            summary.columns = ['Count', 'Success']
                            summary['Success Rate %'] = ((summary['Success'] / summary['Count']) * 100).round(1)
                            summary = summary.fillna(0)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "hourly_analysis":
                            filtered_df['Hour'] = filtered_df['Time'].dt.hour
                            summary = filtered_df.groupby('Hour').agg({
                                'Number': 'count',
                                'Call Status': lambda x: (x == 'completed').sum(),
                                'Analysis.task_completion': lambda x: (x == 'true').sum()
                            })
                            summary.columns = ['Total Calls', 'Completed', 'Success']
                            summary['Success Rate %'] = ((summary['Success'] / summary['Completed']) * 100).round(1)
                            summary = summary.fillna(0)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "daily_analysis":
                            filtered_df['Date'] = filtered_df['Time'].dt.date
                            summary = filtered_df.groupby('Date').agg({
                                'Number': 'count',
                                'Call Status': lambda x: (x == 'completed').sum(),
                                'Duration': 'mean',
                                'Analysis.task_completion': lambda x: (x == 'true').sum()
                            }).round(1)
                            summary.columns = ['Total Calls', 'Completed', 'Avg Duration (s)', 'Success']
                            summary['Success Rate %'] = ((summary['Success'] / summary['Completed']) * 100).round(1)
                            summary = summary.fillna(0)
                            st.dataframe(summary, use_container_width=True)
                            
                        elif table_key == "recent_calls":
                            recent = filtered_df.nlargest(20, 'Time')[
                                ['Number', 'Time', 'Use Case', 'Call Status', 'Duration', 'Analysis.task_completion']
                            ].copy()
                            recent['Time'] = recent['Time'].dt.strftime('%Y-%m-%d %H:%M')
                            st.dataframe(recent, use_container_width=True, hide_index=True)
    
    # Download filtered data
    st.markdown("---")
    st.subheader("💾 Download Filtered Data")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"Current filtered dataset contains {len(filtered_df):,} records")
    with col2:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"filtered_calls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    st.info("👆 Please upload a CSV file to begin analysis")
    
    # Show example of expected format
    st.markdown("### Expected CSV Format")
    st.markdown("""
    The CSV should contain the following columns:
    - **Number**: Phone number
    - **Time**: Timestamp of the call
    - **Use Case**: Use case category
    - **Call Status**: Status (e.g., completed, could_not_connect, call_placed)
    - **Duration**: Call duration in seconds
    - **Analysis.task_completion**: Task completion status (true, false, -)
    - And other optional analysis fields...
    """)
