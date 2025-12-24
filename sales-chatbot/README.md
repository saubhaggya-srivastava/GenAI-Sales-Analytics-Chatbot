# 📊 Sales Data Analysis Chatbot

AI-powered chatbot for analyzing sales data using natural language queries.

## 📝 Project Description

This chatbot allows users to query sales and active stores data from an Excel dataset using natural language. It uses Google Gemini AI to understand questions, Pandas for data processing, and Streamlit for the web interface.

**Capabilities:**

- Answer sales queries (total sales, YoY comparisons, by brand/category/region)
- Answer active stores queries (store counts, YoY comparisons, by brand/category/region)
- Generate interactive charts (bar, line)
- Export results to CSV
- Handle complex queries like "Top 5 brands by sales"

**Dataset:** 22,762 transactions | 2024-2025 | ₹8.3M+ sales | 10 brands | 801 stores

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini (gemini-flash-lite-latest)
- **Data Processing:** Pandas
- **Visualization:** Plotly
- **Data Source:** Excel (.xlsb format)

## 📦 Requirements

- Python 3.8+
- Internet connection (for Gemini API)
- Dependencies listed in `requirements.txt`

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get FREE Gemini API Key

- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy the key

### 3. Configure Environment

```bash
# Create .env file from template
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit .env and add your API key
GEMINI_API_KEY=your-api-key-here
```

### 4. Verify Data File

Ensure `Sales & Active Stores Data.xlsb` is in the `data/` folder

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 💡 Example Queries

**Sales Queries:**

- "What were Biscuits sales in January 2024?"
- "Compare sales between 2024 and 2025"
- "Show me top 5 brands by sales"

**Active Stores Queries:**

- "How many active stores did Delphy have in February 2024?"
- "Top 5 brands by active stores"

## 📁 Project Structure

```
sales-chatbot/
├── app.py              # Main Streamlit application
├── data_loader.py      # Load and cache Excel data
├── ai_extractor.py     # Gemini AI parameter extraction
├── query_engine.py     # Pandas filtering and aggregation
├── visualizer.py       # Plotly chart generation
├── utils.py            # CSV export, error handling
├── data/               # Excel data files
├── requirements.txt    # Python dependencies
├── .env                # API keys (not in git)
└── README.md           # This file
```

## 🐛 Troubleshooting

**"No module named 'streamlit'"**

```bash
pip install -r requirements.txt
```

**"Gemini API key not found"**

- Check `.env` file exists and contains `GEMINI_API_KEY=your-key`
- Get new key from https://makersuite.google.com/app/apikey

**"File not found: data/..."**

- Ensure Excel file is in `data/` folder
- Check file name matches exactly

---

**Author:** Saubhaggya Srivastava 
**Date:** December 2025  
**Tech Stack:** Python | Streamlit | Pandas | Plotly | Google Gemini AI
