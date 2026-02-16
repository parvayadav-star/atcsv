# Call Analysis Dashboard 📞

A comprehensive Streamlit application for analyzing call data with advanced filtering, metrics tracking, and multi-table views.

## Features

### 🔍 Filtering Options
- **Use Case**: Filter by specific use cases
- **Call Status**: Filter by call_placed, completed, could_not_connect, call_canceled
- **Task Completion**: Filter by true/false/- (task success status)
- **Duration Range**: Adjustable slider for call duration filtering
- **Number Exclusion**: Add specific phone numbers to exclude from analysis

### 📊 Key Metrics Dashboard
The app displays 6 key metrics at the top:
1. **Calls Made**: Total number of calls in filtered dataset
2. **Call Placed**: Number of calls with "call_placed" status
3. **Could Not Connect**: Number of calls that couldn't connect
4. **Call Completed**: Number of successfully completed calls
5. **Call Success**: Number of calls where Analysis.task_completion = "true"
6. **Avg Duration**: Average call duration for non-zero duration calls

### 📋 Dynamic Tables (3-5 concurrent views)
Choose from 7 different table types:

1. **Summary by Use Case**
   - Total calls per use case
   - Completed calls
   - Average duration
   - Success count and success rate %

2. **Summary by Call Status**
   - Count per status
   - Average, max, and total duration
   - Percentage distribution

3. **Summary by Task Completion**
   - Count per completion status
   - Average duration
   - Completed calls
   - Percentage distribution

4. **Duration Analysis**
   - Calls grouped by duration buckets (0-10s, 11-30s, 31-60s, 1-2min, 2-5min, 5min+)
   - Success count and success rate per bucket

5. **Hourly Analysis**
   - Calls by hour of day
   - Completed and successful calls per hour
   - Success rate %

6. **Daily Analysis**
   - Calls by date
   - Average duration
   - Success metrics

7. **Recent Calls Detail**
   - Last 20 calls with full details
   - Quick overview of recent activity

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run call_analysis_app.py
   ```

3. **Access the dashboard:**
   The app will automatically open in your browser at `http://localhost:8501`

## Usage

### 1. Upload Data
- Click "Browse files" and upload your CSV file
- The app expects a CSV with these key columns:
  - Number
  - Time
  - Use Case
  - Call Status
  - Duration
  - Analysis.task_completion

### 2. Apply Filters
Use the sidebar to:
- Select specific use cases
- Choose call statuses
- Filter by task completion
- Adjust duration range
- Exclude specific phone numbers

### 3. View Metrics
The top metrics bar updates automatically based on your filters

### 4. Select Tables
Choose 3-5 tables from the dropdown to display:
- Tables appear in a 2-column grid layout
- All tables update dynamically based on filters

### 5. Download Results
Click "Download CSV" to export your filtered dataset

## Data Schema

### Required Columns
- **Number** (string): Phone number
- **Time** (datetime): Call timestamp
- **Use Case** (string): Use case category
- **Call Status** (string): completed, could_not_connect, call_placed, call_canceled
- **Duration** (integer): Call duration in seconds
- **Analysis.task_completion** (string): true, false, or -

### Optional Columns
All other Analysis.* fields are optional and won't affect core functionality

## Tips

### Number Exclusion
- Enter one phone number per line
- Numbers are matched exactly (include country code if present)
- Useful for excluding test numbers or specific contacts

### Duration Filtering
- Duration is in seconds
- 0 duration usually indicates "could not connect" calls
- Use the slider to focus on specific call length ranges

### Success Rate Calculation
- Success Rate % = (Calls with task_completion=true / Completed Calls) × 100
- Only calculated for completed calls
- Shows in Use Case and Hourly/Daily analysis tables

### Table Selection
- Limit to 3-5 tables for optimal viewing
- Tables appear side-by-side in 2-column layout
- Scroll down to see all selected tables

## Troubleshooting

### CSV Upload Issues
- Ensure CSV is UTF-8 encoded
- Check that required columns exist
- Verify Time column is in a parseable datetime format

### Filter Not Working
- Clear filters and reapply
- Check if exclusion list has extra spaces
- Ensure selected values exist in data

### Performance
- For very large datasets (>100k rows), filtering may take a few seconds
- Consider pre-filtering data before upload for faster performance

## Example Workflow

1. Upload `user-calls-2026-02-16.csv`
2. Select use cases of interest (e.g., "long_hault_puneet_main_agent")
3. Filter to only "completed" calls
4. Set duration range to 10-300 seconds (exclude very short/long calls)
5. Add test numbers to exclusion list
6. Select tables: "Summary by Use Case", "Duration Analysis", "Hourly Analysis"
7. Review metrics and success rates
8. Download filtered data for further analysis

## License

This tool is provided as-is for call data analysis purposes.
