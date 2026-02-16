# Call Analysis Dashboard v2 📞

Enhanced Streamlit application with **Nth Call Analysis** and **Modular Table Builder** for advanced call data analytics.

## 🆕 New Features

### 1. 🔢 Nth Call Analysis Section
Complete analysis of call performance by attempt number with three interactive tabs:

#### Tab 1: Call Number Analytics
- Performance metrics by call number (1st call, 2nd call, etc.)
- Shows: Total calls, picked up, goal met, driver negative
- Calculates: Call Pick Rate %, Goal Success on Picked Calls %
- Matches the exact table format from your screenshot
- Downloadable CSV export

#### Tab 2: Pickup Rate Trend
- Interactive line chart showing pickup rate by call attempt
- Visualizes: How pickup rate changes with each subsequent attempt
- Hover data for detailed metrics
- Data table below chart

#### Tab 3: Frequency Heatmaps
Two heatmap options:
- **Total Calls vs Completed Calls**: Shows percentage distribution of users
- **Total Calls vs Task Success**: Analyzes task completion patterns
- Handles 10+ buckets intelligently
- Masks impossible cells (e.g., 5 completed when only 3 total calls)

### 2. 🔧 Modular Table Builder
Create custom pivot tables with complete flexibility:

**Configuration Options:**
- **Row Variable**: Choose what to group by (Use Case, Call Status, Hour, etc.)
- **Column Variable**: Optional - create pivot tables with cross-tabulation
- **Calculated Fields**: Select from 10+ metrics:
  - Count
  - Completed Calls
  - Could Not Connect
  - Task Success Count
  - Task Success %
  - Avg Duration
  - Total Duration
  - Max Duration
  - Negative Sentiment Count
  - Pickup Rate %

**Features:**
- Create 1-5 tables simultaneously
- Each table fully customizable
- Side-by-side display (2 per row)
- Automatic percentage calculations
- Smart aggregation based on selected metrics

## 📊 Original Features (Still Available)

### Filtering Options
- Use Case, Call Status, Task Completion, Duration Range
- Number exclusion list
- Real-time filter summary

### Key Metrics Dashboard
6 core metrics: Calls Made, Call Placed, Could Not Connect, Call Completed, Call Success, Avg Duration

### Data Export
Download filtered datasets and nth call analysis as CSV

## Installation

```bash
pip install -r requirements_v2.txt
```

## Running the App

```bash
streamlit run call_analysis_app_v2.py
```

## Usage Examples

### Example 1: Nth Call Analysis Workflow
```
1. Upload your CSV
2. Apply filters (e.g., specific use case, completed calls only)
3. Navigate to "Nth Call Analysis" section
4. Tab 1: View performance by call number
   - See pickup rates for 1st, 2nd, 3rd attempts
   - Identify optimal number of retry attempts
5. Tab 2: Visualize pickup rate trend
   - See if rate improves or degrades with attempts
6. Tab 3: Analyze user patterns
   - Heatmap shows % of users by call frequency
   - Identify common user behaviors
```

### Example 2: Custom Table Creation
```
1. Go to "Modular Table Builder"
2. Set number of tables to 3
3. Table 1:
   - Row: Use Case
   - Metrics: Count, Pickup Rate %, Task Success %
4. Table 2:
   - Row: Hour
   - Metrics: Completed Calls, Avg Duration
5. Table 3:
   - Row: Call Status
   - Column: Analysis.task_completion
   - Metrics: Count
6. Click "Generate Tables"
7. View all 3 tables side-by-side
```

### Example 3: Reproduce Your Screenshot Table
```
1. Navigate to "Nth Call Analysis"
2. Tab 1: "Call Number Analytics"
3. The table automatically shows:
   - nth call (1, 2, 3, 4...)
   - nth total calls (381, 293, 236, 184...)
   - picked up (272, 190, 146, 116...)
   - Goal met (120, 74, 73, 48...)
   - Driver Negative (20, 18, 7, 18...)
   - Call Pick Rate (71.4%, 64.8%, 61.9%, 63.0%...)
   - Goal Success on Picked Calls (44.1%, 38.9%, 50.0%, 41.4%...)
4. Download as CSV for reporting
```

## Data Schema

### Required Columns
- **Number** (string): Phone number - used to track nth call
- **Time** (datetime): Call timestamp - used for sequencing
- **Use Case** (string): Use case category
- **Call Status** (string): completed, could_not_connect, call_placed, call_canceled
- **Duration** (integer): Call duration in seconds
- **Analysis.task_completion** (string/bool): true, false, or -
- **Analysis.user_sentiment** (string): positive, negative, neutral, or -

### Derived Columns (Auto-created)
- **call_date**: Date extracted from Time
- **Hour**: Hour of day (0-23)
- **DayOfWeek**: Monday, Tuesday, etc.
- **call_number**: Nth call per user (1, 2, 3...)
- **call_attempt**: Same as call_number

## Key Calculations

### Nth Call Metrics
```python
# Call Pick Rate
Call Pick Rate % = (Picked Up / Total Calls for that nth) × 100

# Goal Success on Picked Calls
Goal Success % = (Goal Met / Picked Up) × 100

# These match your notebook calculations exactly
```

### Heatmap Deduplication
```python
# One call per user per day (keeps best attempt)
- Sort by: User, Date, Completed (desc), Time
- Keep: First record per user-date
- This ensures daily frequency isn't inflated by retries
```

## Tips & Best Practices

### For Nth Call Analysis
- **Filter first**: Apply use case/status filters before viewing nth analysis
- **Exclude test numbers**: Add test phone numbers to exclusion list
- **Compare use cases**: Run analysis separately for different use cases
- **Download data**: Export nth call tables for stakeholder reports

### For Modular Tables
- **Start simple**: Begin with 1-2 metrics per table
- **Use row variables meaningfully**: Group by dimensions that matter (Use Case, Hour)
- **Combine metrics**: Pair counts with percentages for context
- **Iterate quickly**: Generate tables, adjust, regenerate

### For Heatmaps
- **Deduplicated data**: Heatmaps use one-call-per-user-per-day to show true frequency
- **Read percentages**: Each cell shows % of users in that row
- **Identify patterns**: Look for diagonal patterns (consistency) vs scattered (variance)

## Performance Notes

- Handles datasets up to 100k rows efficiently
- Nth call calculations may take 2-3 seconds on large datasets
- Heatmaps are pre-filtered for faster rendering
- Table generation is instant (<1 second)

## Troubleshooting

### Nth Call Analysis Shows Wrong Numbers
- Ensure Time column is properly formatted
- Check that Number column has consistent formatting
- Verify filters aren't excluding key records

### Heatmap Not Showing
- Check if filtered data has enough records (min 10)
- Ensure Analysis.task_completion has valid values
- Try different heatmap type (toggle between the two)

### Table Builder Error
- Verify selected metrics are appropriate for row variable
- Don't mix incompatible metrics (e.g., Duration metrics with sentiment row)
- Reduce number of tables if memory issues occur

## Comparison with Notebooks

This Streamlit app implements all the analyses from your Jupyter notebooks:

| Notebook Analysis | Streamlit Location |
|-------------------|-------------------|
| Nth call analytics table | Nth Call Analysis → Tab 1 |
| Pickup rate by attempt | Nth Call Analysis → Tab 2 |
| Calls made vs picked heatmap | Nth Call Analysis → Tab 3 (option 1) |
| Task success heatmap | Nth Call Analysis → Tab 3 (option 2) |
| Custom aggregations | Modular Table Builder |

**Advantages over notebooks:**
- No code required - point and click interface
- Real-time filtering and updates
- Multiple analyses visible simultaneously
- Easy to share (just send the app link)
- Download results directly

## License

This tool is provided as-is for call data analysis purposes.
