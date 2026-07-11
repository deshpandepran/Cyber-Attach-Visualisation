# CS661 Big Data Visual Analytics: Project Architecture & Code Review Report
**Project Name:** CyberVision  
**Course:** CS661 Big Data Visual Analytics  

---

## 1. Repository Analysis

### Folder Structure
The repository is structured as a modular Streamlit multi-page application.
*   `data/`
    *   `raw/`: Contains raw CSV source files.
    *   `processed/`: Holds the preprocessed/cleaned CSV datasets.
*   `src/preprocessing/`: Contains scripts for dataset-specific data cleansing.
*   `backend/`: Contains analytical models, filtering algorithms, data integration schemas, and risk calculation engines.
*   `frontend/`: Manages layout styling, custom CSS assets, sidebar filters, and custom visualization components.
*   `pages/`: Python page modules representing different tabs of the dashboard.
*   `tests/`: Standard unit tests folder.
*   `docs/`: Project documentation and setup guidelines.
*   `app.py`: Root entry point orchestrating layout rendering and page routing.

### Existing Modules
*   `backend/loader.py`: Caches dataset reads from disk using Streamlit's `@st.cache_data`.
*   `backend/integration.py`: Standardizes country names and attack classifications to resolve schemas.
*   `backend/risk.py`: Computes country-specific and sector-specific threat risk indicators.
*   `backend/filters.py`: Selects records from dataframes based on active sidebar controls.
*   `backend/analytics.py`: Performs counts and sums to generate raw KPI values.
*   `frontend/layout.py`: Injects premium glassmorphic dark-theme styles.
*   `frontend/sidebar.py`: Builds sidebar navigation and filter widgets.
*   `frontend/components.py`: Construct Plotly visual structures.

### Missing Modules
*   **Malware Family Analytics Page:** Omitted from the active sidebar due to data imbalance issues in the original dataset.
*   **Predictive Operations Page:** Omitted time-series forecasting (e.g. using Prophet) or threat prediction engines.

### Reusable Code
*   `base_cleaning.py`: Functions for generic column name cleaning and duplicate removal.
*   `frontend/components.py`: Generic Plotly configuration templates and custom metric cards.
*   `backend/risk.py`: MinMax scaling algorithms that can be reused for arbitrary categorical columns.

### Dead / Redundant Code
*   `src/preprocessing/setup_data_fallback.py`: Generates mock datasets. Now redundant as raw files are fully integrated.
*   `dashboards/app.py`: Legacy monolithic code. The root `app.py` has replaced its functionality.

### Duplicate Code
*   Aggregation structures in `backend/analytics.py` (e.g. `groupby("standard_country")`) overlap with the data-grouping routines inside `backend/risk.py`.

### Technical Debt
*   **Hardcoded Weights:** Risk calculation weights are statically declared (Count: 0.3, Loss: 0.4, Time: 0.3) without configuration exposure.
*   **Rigid Maps:** Geolocation mappings rely on an hardcoded dictionary in `backend/integration.py`, omitting standard external ISO-3 code translation libraries.

### Code Quality & Guidelines
*   **Code Quality:** High. Clean function definitions, descriptive docstrings, type annotations, and performance caching.
*   **Files that should NEVER be modified:** All files under `src/preprocessing/` (excluding any bug fixes). Specifically, the cleaning scripts of Pranjali/Khushi must remain untouched to preserve dataset integrity and history.

---

## 2. Dashboard Review

### Page-by-Page UI/UX Review

#### Home Dashboard (`pages/Home.py`)
*   **UI Issues:** KPI cards have fixed margins; layout squishes on narrow desktop resolutions.
*   **UX Issues:** No interactive guides explaining the map's risk score meaning.
*   **Aesthetics:** High-fidelity glassmorphic cards look premium, but default Streamlit spinner contrasts with the custom neon theme.
*   **Performance:** Excellent due to `@st.cache_data` loader.

#### Global Threat Trends (`pages/Global_Threats.py`)
*   **UI Issues:** Symmetrical column charts (`col1`, `col2`) display height mismatches if labels wrap to new lines.
*   **UX Issues:** No legend explaining what the colored lines represent on the attack vectors timeline.
*   **Chart Sizing:** Static heights block responsive layout scaling.

#### World Threat Map (`pages/Country_Map.py`)
*   **UI Issues:** Legend label overlaps the chart on smaller screens.
*   **UX Issues:** Default choropleth colors are dark and make low-risk countries invisible.
*   **Data Integrity:** Replaced/missing values mapped to "Unknown" are ignored in coordinates.

#### Industry Dashboard (`pages/Industry.py`)
*   **UI/UX Issues:** Treemap lacks breadcrumb navigation to trace parent nodes easily.
*   **Color Consistency:** "Viridis" color scale does not match the dashboard's neon color scheme.

#### Vulnerability Explorer (`pages/Vulnerability.py`)
*   **UI Issues:** The heatmap uses a default purple color scheme that breaks visual harmony.
*   **UX Issues:** Top CVE table is cramped and truncates description summaries.

#### Attack Source Dashboard (`pages/Attack_Source.py`)
*   **UI/UX Issues:** The scatter plot displays 1,000 points, but lacks clear annotations explaining what constitutes an anomaly.

#### Threat Relationship Network (`pages/Network.py`)
*   **UI/UX Issues:** The NetworkX visual is projected statically onto a Plotly scatter map; nodes overlap and lack dynamic interactive physics.

---

## 3. Backend Review
*   **Data Pipeline:** The loader runs perfectly. Caching is used for all load operations.
*   **Standardization:** Mapping is robust but limited to 14 hardcoded countries. Other countries standardizing via `.title()` might cause duplicates (e.g. "united arab emirates" becomes "United Arab Emirates", but standard mappings might prefer "UAE").
*   **Memory Efficiency:** Pandas dataframes are fully loaded in memory, which is acceptable for ~100k rows but could be optimized.

---

## 4. Frontend Review
*   **Theme Integration:** The CSS injection in `layout.py` sets background, layout padding, and custom card shapes.
*   **Grid System:** Streamlit's `st.columns` is responsive but lacks flexbox properties.
*   **Accessibility:** Contrast levels on neon elements are excellent. Hover effects provide helpful visual cues.

---

## 5. Visualization Review

| Visualization | Representation | Appropriateness | Suggested Improvement |
| :--- | :--- | :--- | :--- |
| **Global Area Trend** | Annual attack count progression. | Highly Appropriate | Add prediction trendlines. |
| **Risk Choropleth** | Geopolitical risk map. | Appropriate | Change color map to neon gradient. |
| **Industry Treemap** | Financial loss by commercial sector. | Highly Appropriate | Add hover information with percentage contributions. |
| **Vulnerability Heatmap**| Year vs Severity density. | Appropriate | Change color map to sync with theme. |
| **Intrusion Scatter** | Network anomalies vs packet sizes. | Moderate | Highlight outliers with red alert boundaries. |
| **Relationship Network** | Threat source, country, industry connections. | Moderate | Implement physics-based layout. |

---

## 6. Feature Engineering Review

### Country & Industry Risk Index
The risk score ($R$) for any entity is computed as a weighted sum of normalized incident counts ($N$), average financial losses ($L$), and average incident resolution times ($T$):

$$R = \left( w_1 \cdot \bar{N} + w_2 \cdot \bar{L} + w_3 \cdot \bar{T} \right) \times 10$$

Where the features are scaled using MinMax normalization:

$$\bar{X} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

And weights are set to:
*   $w_1 = 0.3$ (Incident frequency)
*   $w_2 = 0.4$ (Economic damage impact)
*   $w_3 = 0.3$ (Response operational time)

---

## 7. Report Review

### Deep-Dive Analysis of Visualizations

#### Global Threat Volume Trend (Task 4.1)
*   **Overview:** Maps annual cyber incidents.
*   **Observed Trends:** Attack frequencies surged in 2017 and peaked in 2022.
*   **Inference & Insights:** This pattern correlates with major global events (e.g. ransomware outbreaks like WannaCry in 2017, and geopolitical tensions in 2022).
*   **Real World Implications:** Organizations must scale up security investments during periods of high geopolitical tension.

#### Global Security Risk Map (Task 4.2)
*   **Overview:** Geopolitical distribution of threats.
*   **Observed Trends:** High risk indexes are registered in North America, Europe, and Australia.
*   **Inference & Insights:** Highly digitized economies face greater exposure to threat actors.
*   **Real World Implications:** Cyber defense resources must align with digital footprint sizes.

#### Industry Impact Profile (Task 4.3)
*   **Overview:** Treemap showing sector targeting.
*   **Observed Trends:** Healthcare and Finance represent the highest total financial losses.
*   **Inference & Insights:** Healthcare has high recovery costs, while Finance represents direct monetary theft targets.
*   **Real World Implications:** Sector-specific regulations must enforce zero-trust policies.

#### Vulnerability Severity Density (Task 4.4)
*   **Overview:** Annual CVE severity trends.
*   **Observed Trends:** Critical and High severity CVE count has expanded since 2020.
*   **Inference & Insights:** Acceleration of cloud migration has expanded system attack surfaces.
*   **Real World Implications:** Vulnerability patch cycles must prioritize critical assets.

#### Malware Family Analytics (Task 4.5)
*   **Overview:** Forensics of malware category distribution.
*   **Evaluation:** The original dataset is heavily dominated by a single category. To remain consistent, the dashboard presents a broad class balance overview (Benign vs Malicious) rather than trying to force detailed sub-family analytics.

#### Intrusion Signatures Matrix (Task 4.6)
*   **Overview:** Network traffic forensics.
*   **Observed Trends:** High packet lengths show a strong correlation with high anomaly scores.
*   **Inference & Insights:** Large payloads often carry exploit signatures or exfiltrated data.
*   **Real World Implications:** Automated firewall filters should inspect large packets closely.

#### Geopolitical Relationship Network (Task 4.7)
*   **Overview:** Multi-entity connection mapping.
*   **Observed Trends:** Nation-states show high degree connectivity with critical energy sectors.
*   **Inference & Insights:** Advanced Persistent Threats (APTs) focus on national infrastructure.
*   **Real World Implications:** Public-private partnerships are crucial to protect core infrastructure.

---

## 8. Proposal Compliance

| Proposal Task | Current Status | Missing | Priority | Responsible Member |
| :--- | :--- | :--- | :--- | :--- |
| **4.1 Global Trend** | Fully Completed | None | High | Nikita Nehra / Haryashva |
| **4.2 Country Map** | Fully Completed | None | High | Namrata / Vivekananda |
| **4.3 Industry Risk** | Fully Completed | None | High | Mayank / Vishesh |
| **4.4 Vuln Explorer**| Fully Completed | None | High | Pranjali / Khushi |
| **4.5 Malware Family**| Handled (Class) | Sub-family detail | Medium | Mayank / Vishesh |
| **4.6 Attack Source** | Fully Completed | None | High | Nikita Nehra / Haryashva |
| **4.7 Threat Network**| Fully Completed | None | High | Namrata / Vivekananda |

---

## 9. Missing Components
*   **Predictive Alert Engine:** Lacks forecasting on future alert counts.
*   **Vulnerability Severity Score:** Standard CVE CVSS scores could be used to weight vulnerability impact in risk calculations.

---

## 10. Suggested Improvements
1.  **Modular CSS:** Decouple CSS styles from `layout.py` into a separate stylesheet.
2.  **Interactive Network Graphs:** Replace standard scatter network charts with physics-based representations.
3.  **Enhanced Risk Scoring:** Integrate CVSS severity levels into the global Country Risk Index.

---

## 11. Exact Files to Modify

*   **[MODIFY]** `frontend/layout.py`: Inject improved theme styling rules.
*   **[MODIFY]** `frontend/components.py`: Tweak color schemes to match the neon styling.
*   **[MODIFY]** `backend/risk.py`: Standardize normalization algorithms.

---

## 12. Git Commit Sequence

1.  `[viz] improve frontend theme styles and layout spacing`
2.  `[viz] refine plotly colors and styling parameters`
3.  `[viz] enhance risk score normalization parameters`

---

## 13. Final Submission Checklist
*   [x] Preprocessing pipelines are locked.
*   [x] Cleaned datasets match proposal schemas.
*   [x] Streamlit dashboard successfully deployed.
*   [x] Visualizations align with course guidelines.
*   [x] All team contributions are preserved.
