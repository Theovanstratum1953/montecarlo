# 🎲 The Risk Horizon: Probabilistic Delivery Suite

**Stop Guessing. Start Calculating.**

The Risk Horizon is a project management tool that replaces subjective "Story Points" with Monte Carlo simulations. It provides actuarial precision for forecasting delivery dates, helping you manage uncertainty and set realistic expectations.

Theo van Stratum PhD

---

## ✨ Key Features

- **Delivery Forecast (Pre-Project Strategy):** Calculate the probability of completing a defined scope within a certain timeframe based on historical throughput.
- **Risk Horizon (Active Project Tactics):** Track active projects using a dynamic Burn-up chart and "Cone of Uncertainty" that narrows as you collect more data.
- **Monte Carlo Simulations:** Run thousands of simulations to generate statistically significant delivery dates.
- **PDF Report Generation:** Export your findings into professional reports for stakeholders.
- **Privacy First:** Keep your project data local and secure.

---

## 🚀 Getting Started

### Option 1: Try the Demo
Test the tool instantly with dummy data:
[**Launch Web App**](https://your-app-url.streamlit.app)

---

### Option 2: Run Locally (Recommended)

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

#### Quick Start with Docker
1. Clone this repository:
   ```bash
   git clone https://github.com/yourname/risk-horizon.git
   cd risk-horizon
   ```
2. Start the application:
   ```bash
   docker-compose up --build
   ```
3. Open your browser and navigate to `http://localhost:8501`.

#### Manual Installation (Alternative)
If you prefer to run without Docker:
1. Ensure you have **Python 3.9+** installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

---

## 🛠 Usage Guide

### 1. Delivery Forecast
Use this for **Pre-Project Strategy**.
- **Input:** Your best and worst-case scope (Min/Max items) and your team's historical throughput (items per week).
- **Output:** A Probability Histogram showing the likelihood of finishing by various dates.

### 2. Risk Horizon
Use this for **Active Projects**.
- **Input:** Total scope and weekly actual throughput.
- **Output:** A Burn-up chart with a projection cone showing the most likely completion dates based on current velocity.

---

## 📥 Importing Data

Both the **Delivery Forecast** and **Risk Horizon** tools allow you to import data instead of manual entry. You can upload your team's historical throughput (**Pulse**) or current project progress (**Actuals**).

### Supported Formats
- **CSV** (`.csv`)
- **Excel** (`.xlsx`)

### File Structure
The tool is designed for simplicity. It reads the **first column** of your file and expects each row to contain an integer representing the number of items completed in a single week.

| Week | Throughput (Items) |
| :--- | :--- |
| Week 1 | 5 |
| Week 2 | 3 |
| Week 3 | 6 |
| Week 4 | 4 |

> **Note:** The header row is optional. The tool will skip non-numeric values and focus on the first column.

### Example CSV
Create a file named `pulse.csv` with the following content:
```csv
Items
5
3
6
4
7
```

### Where to upload?
1.  Navigate to **Delivery Forecast** or **Risk Horizon**.
2.  Look for the **Upload Data** or **Upload Pulse/Actuals** tabs.
3.  Drag and drop your file into the uploader.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the tool.

