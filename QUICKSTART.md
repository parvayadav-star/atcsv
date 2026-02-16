# Quick Start Guide 🚀

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run call_analysis_app.py
```

### Step 3: Upload & Analyze
1. Open the app in your browser (opens automatically)
2. Upload your CSV file
3. Use filters in the sidebar
4. Select 3-5 tables to view
5. Download filtered results

## Key Features Summary

✅ **Filters**: Use Case, Call Status, Task Completion, Duration Range  
✅ **Exclusions**: Add numbers to exclude from analysis  
✅ **Metrics**: 6 key metrics displayed at top  
✅ **Tables**: Choose 3-5 concurrent table views  
✅ **Download**: Export filtered data as CSV  

## Your Data Schema

Based on your uploaded file:
- **2,183 total records**
- **Use Cases**: 10 different use cases (long_hault_puneet_main_agent, sample_test_9, etc.)
- **Call Statuses**: could_not_connect, completed, call_placed, call_canceled
- **Task Completion**: true, false, - (none)
- **Duration Range**: 0 to 416 seconds

## Example Analysis Workflow

```
1. Upload: user-calls-2026-02-16.csv
2. Filter: Select "completed" calls only
3. Duration: Set to 10-300 seconds
4. Exclude: Add test numbers (one per line)
5. Tables: Choose:
   - Summary by Use Case
   - Duration Analysis  
   - Hourly Analysis
   - Call Status Summary
   - Recent Calls Detail
6. Review: Check success rates and patterns
7. Download: Export filtered dataset
```

## Need Help?

See `README.md` for detailed documentation.
