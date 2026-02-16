import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
    
    # Normalize columns
    df['Analysis.task_completion'] = (
        df['Analysis.task_completion']
        .astype(str)
        .str.lower()
        .map({'true': True, 'false': False, 'True': True, 'False': False})
    )
    
    df['Analysis.user_sentiment'] = (
        df['Analysis.user_sentiment']
        .astype(str)
        .str.lower()
        .replace({'n.a': None, '-': None, 'nan': None})
    )
    
    # Create derived columns
    df['call_date'] = df['Time'].dt.date
    df['Hour'] = df['Time'].dt.hour
    df['DayOfWeek'] = df['Time'].dt.day_name()
    
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
    task_completions = [True, False, None]
    task_completion_labels = {True: "True", False: "False", None: "N/A"}
    selected_completions_labels = st.sidebar.multiselect(
        "Select Task Completion",
        options=[task_completion_labels[x] for x in task_completions],
        default=[task_completion_labels[x] for x in task_completions],
        help="Filter by task completion status"
    )
    
    # Map back to actual values
    label_to_value = {v: k for k, v in task_completion_labels.items()}
    selected_completions = [label_to_value[label] for label in selected_completions_labels]
    
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
    task_success = len(filtered_df[filtered_df['Analysis.task_completion'] == True])
    
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
    
    # ==========================================
    # NTH CALL ANALYSIS SECTION
    # ==========================================
    st.markdown("---")
    st.header("🔢 Nth Call Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Call Number Analytics", "📈 Pickup Rate by Attempt", "🔥 Frequency Heatmap"])
    
    with tab1:
        st.subheader("Performance by Call Number")
        
        # Assign call number per user
        analysis_df = filtered_df.copy()
        analysis_df = analysis_df.sort_values(by=['Number', 'Time'])
        analysis_df['call_number'] = analysis_df.groupby('Number').cumcount() + 1
        
        # Build analytics table - INCLUDING all call statuses
        nth_analytics = (
            analysis_df.groupby('call_number')
            .agg(
                total_calls=('call_number', 'count'),
                picked_up=('Call Status', lambda x: (x == 'completed').sum()),
                goal_met=('Analysis.task_completion', lambda x: (x == True).sum()),  # Only True, not fillna
                negative_sentiment=('Analysis.user_sentiment', lambda x: (x == 'negative').sum()),
            )
            .reset_index()
        )
        
        # Calculate rates
        nth_analytics['Call Pick Rate'] = (nth_analytics['picked_up'] / nth_analytics['total_calls'] * 100).round(1)
        nth_analytics['Goal Success on Picked Calls'] = (
            (nth_analytics['goal_met'] / nth_analytics['picked_up'] * 100)
            .replace([np.inf, -np.inf], 0)
            .fillna(0)
            .round(1)
        )
        nth_analytics['Driver Negative'] = nth_analytics['negative_sentiment']
        
        # Rename for display
        display_nth = nth_analytics.rename(columns={
            'call_number': 'nth call',
            'total_calls': 'nth total calls',
            'picked_up': 'picked up',
            'goal_met': 'Goal met'
        })
        
        # Reorder columns to match image
        display_nth = display_nth[[
            'nth call', 'nth total calls', 'picked up', 'Goal met', 
            'Driver Negative', 'Call Pick Rate', 'Goal Success on Picked Calls'
        ]]
        
        st.dataframe(display_nth, use_container_width=True, hide_index=True)
        
        # Add download button
        csv = display_nth.to_csv(index=False)
        st.download_button(
            label="Download Nth Call Analysis",
            data=csv,
            file_name=f"nth_call_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Pickup Rate Trend by Call Attempt")
        
        # Calculate pickup rate by attempt - INCLUDING all call statuses
        analysis_df = filtered_df.copy()
        analysis_df = analysis_df.sort_values(by=['Number', 'Time'])
        analysis_df['call_attempt'] = analysis_df.groupby('Number').cumcount() + 1
        
        attempt_funnel = (
            analysis_df.groupby('call_attempt')
            .agg(
                attempts=('Call Status', 'count'),  # All attempts
                completed=('Call Status', lambda x: (x == 'completed').sum())  # Only completed
            )
            .reset_index()
        )
        
        attempt_funnel['pickup_rate_pct'] = (
            attempt_funnel['completed'] / attempt_funnel['attempts'] * 100
        ).round(1)
        
        # Plot
        fig = px.line(
            attempt_funnel, 
            x='call_attempt', 
            y='pickup_rate_pct',
            markers=True,
            labels={'call_attempt': 'Call Attempt Number', 'pickup_rate_pct': 'Pickup Rate (%)'},
            title='Pickup Rate by Call Attempt Number'
        )
        fig.update_traces(line_color='#1f77b4', marker=dict(size=8))
        fig.update_layout(hovermode='x unified')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show data table
        st.dataframe(
            attempt_funnel.rename(columns={
                'call_attempt': 'Attempt', 
                'attempts': 'Total Attempts',
                'completed': 'Completed',
                'pickup_rate_pct': 'Pickup Rate %'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with tab3:
        st.subheader("User Call Frequency Heatmap")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            heatmap_type = st.radio(
                "Select heatmap type:",
                ["Total Calls vs Completed Calls", "Total Calls vs Task Success"],
                horizontal=True
            )
        with col2:
            deduplicate = st.checkbox(
                "Deduplicate (1 call/user/day)", 
                value=False,
                help="Enable to count only one call per user per day (keeps best attempt)"
            )
        
        # Use all calls or deduplicate based on toggle
        heatmap_df = filtered_df.copy()
        
        if deduplicate:
            st.info("📌 Deduplication enabled: Keeping one call per user per day (prioritizing completed calls)")
            heatmap_df['completed_flag'] = (heatmap_df['Call Status'] == 'completed').astype(int)
            
            heatmap_df = (
                heatmap_df.sort_values(
                    by=['Number', 'call_date', 'completed_flag', 'Time'],
                    ascending=[True, True, False, True]
                )
                .drop_duplicates(subset=['Number', 'call_date'], keep='first')
            )
        else:
            st.info("📌 All calls included: Every call attempt is counted")
        
        if heatmap_type == "Total Calls vs Completed Calls":
            # User-level aggregation - ALL calls included
            user_summary = (
                heatmap_df.groupby('Number')
                .agg(
                    total_calls=('Number', 'count'),  # All calls
                    completed_calls=('Call Status', lambda x: (x == 'completed').sum())  # Only completed
                )
                .reset_index()
            )
            
            # Create 10+ bucket
            user_summary['total_calls_bucket'] = user_summary['total_calls'].clip(upper=10)
            user_summary['completed_calls_bucket'] = user_summary['completed_calls'].clip(upper=10)
            
            # Frequency table
            freq_table = (
                user_summary
                .groupby(['total_calls_bucket', 'completed_calls_bucket'])
                .size()
                .reset_index(name='user_count')
            )
            
            # Pivot + percentages
            heatmap_pivot = freq_table.pivot(
                index='total_calls_bucket',
                columns='completed_calls_bucket',
                values='user_count'
            ).fillna(0)
            
            heatmap_pct = heatmap_pivot.div(heatmap_pivot.sum(axis=1), axis=0) * 100
            
            # Create mask for impossible cells
            mask = np.zeros_like(heatmap_pct, dtype=bool)
            for i, total_calls in enumerate(heatmap_pct.index):
                for j, completed_calls in enumerate(heatmap_pct.columns):
                    if completed_calls > total_calls:
                        mask[i, j] = True
            
            # Apply mask
            heatmap_pct_masked = heatmap_pct.copy()
            heatmap_pct_masked[mask] = np.nan
            
            # Plot
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_pct_masked.values,
                x=[f"{int(x)}" for x in heatmap_pct_masked.columns],
                y=[f"{int(x)}" if x < 10 else "10+" for x in heatmap_pct_masked.index],
                colorscale='YlGnBu',
                text=heatmap_pct_masked.values.round(1),
                texttemplate='%{text:.1f}%',
                textfont={"size": 10},
                colorbar=dict(title="Percentage (%)")
            ))
            
            fig.update_layout(
                title='Percentage of Calls Picked Up per Total Calls Made',
                xaxis_title='Calls Picked Up (Completed)',
                yaxis_title='Total Calls Made',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:  # Task Success heatmap
            # User-level aggregation - ALL calls included
            user_summary = (
                heatmap_df.groupby('Number')
                .agg(
                    total_calls=('Number', 'count'),  # All calls
                    task_true_completed=('Analysis.task_completion', lambda x: (x == True).sum())  # Only True
                )
                .reset_index()
            )
            
            # Create 10+ bucket for total_calls
            user_summary['total_calls_bucket'] = user_summary['total_calls'].apply(
                lambda x: "10+" if x >= 10 else str(x)
            )
            
            # Frequency table
            freq_table = (
                user_summary
                .groupby(['total_calls_bucket', 'task_true_completed'])
                .size()
                .reset_index(name='user_count')
            )
            
            # Pivot + percentages
            heatmap_pivot = freq_table.pivot(
                index='total_calls_bucket',
                columns='task_true_completed',
                values='user_count'
            ).fillna(0)
            
            # Sort index properly
            numeric_indices = [i for i in heatmap_pivot.index if i != "10+"]
            ordered_index = sorted(numeric_indices, key=int)
            if "10+" in heatmap_pivot.index:
                ordered_index.append("10+")
            heatmap_pivot = heatmap_pivot.loc[ordered_index]
            
            heatmap_pct = heatmap_pivot.div(heatmap_pivot.sum(axis=1), axis=0) * 100
            
            # Create mask for impossible cells
            mask = np.zeros_like(heatmap_pct, dtype=bool)
            for i, total_calls in enumerate(heatmap_pct.index):
                max_calls = 10 if total_calls == "10+" else int(total_calls)
                for j, task_true_calls in enumerate(heatmap_pct.columns):
                    if task_true_calls > max_calls:
                        mask[i, j] = True
            
            # Apply mask
            heatmap_pct_masked = heatmap_pct.copy()
            heatmap_pct_masked[mask] = np.nan
            
            # Plot
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_pct_masked.values,
                x=[f"{int(x)}" for x in heatmap_pct_masked.columns],
                y=heatmap_pct_masked.index.tolist(),
                colorscale='YlGnBu',
                text=heatmap_pct_masked.values.round(1),
                texttemplate='%{text:.1f}%',
                textfont={"size": 10},
                colorbar=dict(title="Percentage (%)")
            ))
            
            fig.update_layout(
                title='Task Analysis: Task=True vs Call Frequency',
                xaxis_title='Completed Calls with Task = True',
                yaxis_title='Total Calls Picked',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ==========================================
    # MODULAR TABLE BUILDER
    # ==========================================
    st.markdown("---")
    st.header("🔧 Modular Table Builder")
    
    st.markdown("""
    Create custom pivot tables by selecting:
    - **Row Variable**: What to group by (rows)
    - **Column Variable**: What to break down by (columns) - optional
    - **Calculated Fields**: Metrics to calculate
    """)
    
    # Number of tables to create
    num_tables = st.number_input("Number of tables to create", min_value=1, max_value=5, value=3)
    
    # Available columns for grouping
    categorical_cols = [
        'Use Case', 'Call Status', 'Analysis.task_completion', 
        'Analysis.user_sentiment', 'Hour', 'DayOfWeek'
    ]
    
    # Available calculated fields
    calc_field_options = {
        'Count': lambda x: x.count(),
        'Completed Calls': lambda x: (x == 'completed').sum() if x.name == 'Call Status' else 0,
        'Could Not Connect': lambda x: (x == 'could_not_connect').sum() if x.name == 'Call Status' else 0,
        'Task Success Count': lambda x: x.fillna(False).sum() if x.name == 'Analysis.task_completion' else 0,
        'Task Success %': 'custom',  # Handle separately
        'Avg Duration': lambda x: x.mean() if x.name == 'Duration' else 0,
        'Total Duration': lambda x: x.sum() if x.name == 'Duration' else 0,
        'Max Duration': lambda x: x.max() if x.name == 'Duration' else 0,
        'Negative Sentiment Count': lambda x: (x == 'negative').sum() if x.name == 'Analysis.user_sentiment' else 0,
        'Pickup Rate %': 'custom',
    }
    
    # Create table configurations
    table_configs = []
    for i in range(num_tables):
        with st.expander(f"📊 Table {i+1} Configuration", expanded=(i==0)):
            col1, col2 = st.columns(2)
            
            with col1:
                row_var = st.selectbox(
                    "Row Variable",
                    options=categorical_cols,
                    key=f"row_{i}"
                )
            
            with col2:
                use_col_var = st.checkbox("Use Column Variable", key=f"use_col_{i}")
                if use_col_var:
                    col_var = st.selectbox(
                        "Column Variable",
                        options=[c for c in categorical_cols if c != row_var],
                        key=f"col_{i}"
                    )
                else:
                    col_var = None
            
            # Select metrics
            selected_metrics = st.multiselect(
                "Select Calculated Fields",
                options=list(calc_field_options.keys()),
                default=['Count', 'Pickup Rate %'],
                key=f"metrics_{i}"
            )
            
            table_configs.append({
                'row_var': row_var,
                'col_var': col_var,
                'metrics': selected_metrics
            })
    
    # Generate tables button
    if st.button("Generate Tables", type="primary"):
        st.markdown("---")
        
        # Display tables side by side (2 per row)
        for i in range(0, len(table_configs), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(table_configs):
                    config = table_configs[i + j]
                    
                    with col:
                        st.subheader(f"Table {i+j+1}")
                        
                        try:
                            # Build the table based on configuration
                            if config['col_var'] is None:
                                # Simple groupby
                                agg_dict = {}
                                
                                for metric in config['metrics']:
                                    if metric == 'Count':
                                        agg_dict['Number'] = 'count'
                                    elif metric == 'Completed Calls':
                                        agg_dict['Completed'] = ('Call Status', lambda x: (x == 'completed').sum())
                                    elif metric == 'Could Not Connect':
                                        agg_dict['Could Not Connect'] = ('Call Status', lambda x: (x == 'could_not_connect').sum())
                                    elif metric == 'Task Success Count':
                                        agg_dict['Task Success'] = ('Analysis.task_completion', lambda x: (x == True).sum())
                                    elif metric == 'Avg Duration':
                                        agg_dict['Avg Duration (s)'] = ('Duration', 'mean')
                                    elif metric == 'Total Duration':
                                        agg_dict['Total Duration (s)'] = ('Duration', 'sum')
                                    elif metric == 'Max Duration':
                                        agg_dict['Max Duration (s)'] = ('Duration', 'max')
                                    elif metric == 'Negative Sentiment Count':
                                        agg_dict['Negative Sentiment'] = ('Analysis.user_sentiment', lambda x: (x == 'negative').sum())
                                
                                if agg_dict:
                                    result = filtered_df.groupby(config['row_var']).agg(**agg_dict).round(1)
                                    
                                    # Add calculated percentages
                                    if 'Pickup Rate %' in config['metrics'] and 'Completed' in result.columns:
                                        result['Pickup Rate %'] = (
                                            (result['Completed'] / result.get('Number', result['Completed'])) * 100
                                        ).round(1)
                                    
                                    if 'Task Success %' in config['metrics'] and 'Task Success' in result.columns and 'Completed' in result.columns:
                                        result['Task Success %'] = (
                                            (result['Task Success'] / result['Completed']) * 100
                                        ).fillna(0).round(1)
                                    
                                    st.dataframe(result, use_container_width=True)
                                else:
                                    st.warning("Please select at least one metric")
                            
                            else:
                                # Pivot table
                                if 'Count' in config['metrics']:
                                    result = pd.crosstab(
                                        filtered_df[config['row_var']],
                                        filtered_df[config['col_var']],
                                        margins=True,
                                        margins_name='Total'
                                    )
                                    st.dataframe(result, use_container_width=True)
                                else:
                                    st.info("Pivot tables currently support Count metric. More coming soon!")
                        
                        except Exception as e:
                            st.error(f"Error generating table: {str(e)}")
    
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
