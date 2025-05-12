# Sampling & Exploration Dashboard

This repository contains a Streamlit application for data sampling, exploration, and visualization. It supports loading data from Excel or CSV, provides descriptive statistics and charts, and implements sampling methods including Simple Random Sampling (SRS) and Proportional Stratified Sampling.

---

## 🚀 Features

* **Data Loading**: Load default or user-uploaded Excel (`.xlsx`) or CSV (`.csv`) files.
* **Introduction Tab**: Overview of app capabilities and workflow.
* **Dashboard Tab**: Summary metrics, pie chart of the first column, and raw data preview.
* **Exploratory Analysis Tab**:

  * Descriptive statistics (including numeric and categorical).
  * Histograms with boxplots for numeric variables.
  * Bar charts for categorical variables.
* **Simple Random Sampling (SRS)**:

  * Specify sample size.
  * Compare population vs sample distributions.
  * Download sampled data as CSV.
* **Stratified Sampling**:

  * Proportional allocation based on strata.
  * Optional auxiliary variable summaries.
  * View allocation table, bar chart, and descriptive stats.
  * Download stratified sample as CSV.

---

## 📦 Repository Structure

```plaintext
├── app.py                  # Main Streamlit application
├── data                   # Folder for default datasets
│   └── Cadre Tunisie.xlsx
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

---

## 🛠️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/dridi1/ProjectSondage.git
   cd ProjectSondage
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on macOS/Linux
   venv\Scripts\activate    # on Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Usage

* Access the app in your browser at `http://localhost:8501` or `https://projectsondage.streamlit.app/`.
* Use the sidebar to upload your own data (Excel/CSV) or rely on the default dataset.
* Navigate through tabs to explore data, generate samples, and download results.

---

## 🔧 Configuration

* **Page settings**: Defined in `st.set_page_config` (title, layout, sidebar state).
* **Data caching**: Implemented via `@st.cache_data` to speed up repeated loads.
* **Default file path**: `data/Cadre Tunisie.xlsx`.

---

## 🙌 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for new features, bug fixes, or improvements.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Last updated: May 12, 2025*
