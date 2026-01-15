# Municipal Credit Assessment Dashboard

A web-based dashboard application for visualizing and interacting with municipal creditworthiness assessment data, built using the **PAS (Performance Assessment System) Creditworthiness Framework**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Overview

This application provides a digital implementation of the PAS Creditworthiness Assessment Framework, designed to help Urban Local Bodies (ULBs) in India understand and improve their creditworthiness. It includes:

- Interactive dashboard with key metrics and visualizations
- Financial ratio analysis
- Operating/service level performance tracking
- Year-over-year comparison
- Data input forms for assessment

## Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Overview of creditworthiness scores, grades, and trend charts |
| **Financial Analysis** | Income ratios, expense ratios, leverage analysis with interactive charts |
| **Operating Performance** | Service coverage metrics (Water, SWM, Sanitation, Toilet) |
| **Year Comparison** | Side-by-side comparison across multiple years (2022-2025) |
| **Data Input** | Forms to enter and modify municipal financial and operational data |
| **Rating Scale** | Visual rating from PAS AAA to PAS D with status indicators |

## Scoring Methodology

The creditworthiness score is calculated using:
- **70%** Financial Performance Score
- **30%** Operating/Service Level Score

### Rating Scale

| Grade | Score Range | Status |
|-------|-------------|--------|
| PAS AAA | 90-100 | Highest level of creditworthiness |
| PAS AA | 80-90 | High level of creditworthiness |
| PAS A | 60-80 | Adequate level of creditworthiness |
| PAS BBB | 50-60 | Moderate level of creditworthiness |
| PAS BB | 40-50 | High level of Credit Risk |
| PAS B | 30-40 | Very High level of Credit Risk |
| PAS C | 20-30 | Very High level of Credit Risk |
| PAS D | 0-20 | Not creditworthy |

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yoji-toriumi/Municipal_Credit_Assessment.git
cd Municipal_Credit_Assessment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

### Running in Google Colab

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install dependencies
!pip install streamlit plotly openpyxl

# Run the app (use localtunnel or ngrok to expose)
!streamlit run /content/drive/MyDrive/Municipal_Credit_Assessment/app.py --server.port 8501 &

# Expose using localtunnel
!npm install -g localtunnel
!lt --port 8501
```

## Project Structure

```
Municipal_Credit_Assessment/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── utils/
│   ├── __init__.py
│   ├── data_loader.py     # Excel data extraction utilities
│   └── calculations.py    # Score calculation logic
└── data/
    └── CWAS - Creditworthiness DIY Tool-Trichy.xlsm  # Sample data
```

## Data Source

The sample data is from the **CWAS (Creditworthiness Assessment System) DIY Tool** for **Tiruchirappalli City Municipal Corporation**, Tamil Nadu, India.

### Key Metrics (2024)

- **Total Score**: 60.15/100
- **Grade**: PAS A (Adequate level of creditworthiness)
- **Financial Score**: 60/100
- **Operating Score**: 60.5/100
- **Borrowing Capacity**: Rs. 231.69 Crores

## Screenshots

*Dashboard showing creditworthiness scores and trends*

## Technologies Used

- **Streamlit** - Web application framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **OpenPyXL** - Excel file handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PAS (Performance Assessment System) Framework
- CRDF (City Development Finance) for the assessment methodology
- Tiruchirappalli City Municipal Corporation for sample data

## Contact

For questions or feedback, please open an issue on GitHub.
