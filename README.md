# Rent-to-Price Causal Analysis Dashboard

Interactive dashboard for exploring state-level causal effects of rental price growth on home price appreciation.

## 📁 Project Structure

```
Dashboard/
├── dashboard.py          # Main Streamlit application
├── requirements.txt      # Python dependencies
├── setup.py             # Cross-platform setup script (Python)
├── run.bat              # Windows one-click launcher
├── run.sh               # Mac/Linux one-click launcher
├── README.md            # This file
├── Model/
│   └── causal_forest_model.joblib
└── Resources/
    ├── causal_forest_results.csv
    ├── state_mapping.csv
    ├── feature_importance.csv
    └── summary_stats.joblib
```

## 🚀 Quick Start

### Windows Users
Simply double-click `run.bat` — it will:
1. Create a virtual environment
2. Install all dependencies
3. Launch the dashboard

### Mac/Linux Users
Open terminal in this folder and run:
```bash
chmod +x run.sh   # Make executable (first time only)
./run.sh
```

### Alternative: Python Script (Cross-platform)
```bash
python setup.py
```

## 🔧 Manual Setup

If the automatic scripts don't work, follow these steps:

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Dashboard
```bash
streamlit run dashboard.py
```

### 4. Open Browser
Navigate to: http://localhost:8501

## 📊 Features

- **State-Level Treatment Effects**: Explore CATE estimates for each U.S. state
- **Effect Simulator**: Predict treatment effects under different market conditions
- **Impact Calculator**: Translate percentage effects to dollar amounts
- **Heterogeneity Analysis**: Visualize how supply elasticity moderates effects

## ⚙️ Requirements

- Python 3.8 or higher
- ~500MB disk space for dependencies
- Modern web browser

## 🛑 Stopping the Dashboard

Press `Ctrl+C` in the terminal window to stop the server.

## 📝 Notes

- First run may take a few minutes to install dependencies
- The dashboard caches model predictions for performance
- All data is processed locally — no internet required after setup

## 📧 Contact

For questions about the research methodology, refer to the main paper:
"Estimation of State-Level Causal Effects of Rental Prices on Home Values 
in the United States Using Causal Machine Learning"

---
*Far Eastern University - Manila | Machine Learning Final Project | December 2025*
