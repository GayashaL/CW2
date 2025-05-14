import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px 
import numpy as np
import base64 





df=pd.read_csv("preprocessed_dataset.csv")

#set style
sns.set(style="whitegrid")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()



# configure streamlit page
st.set_page_config(page_title="World Development Indicators", layout="wide")
st.title("World Development Indicators : Sri Lanka")

# Set background image using CSS
page_bg_img = '''
<style>
.stApp {
    background-image: url("istockphoto-170618801-170667a.jpg"); /* Replace with your URL */
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)





img_base64 = get_base64_of_bin_file('istockphoto-170618801-170667a.jpg')  
page_bg_img = f'''
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)



with st.sidebar.markdown("ℹ About this Dashboard"):
    st.sidebar.info("""
    This interactive dashboard presents a comprehensive analysis of **Sri Lanka’s development journey** from **1960 to 2025**, using data from the World Bank's **World Development Indicators (WDI)** dataset.

    The dashboard enables students, researchers, analysts, and policymakers to explore long-term trends in Sri Lanka’s **economic, social, environmental, and financial indicators**.

    **Key Indicator Categories Included:**
    - **Economic metrics** such as GDP, inflation, and savings
    - **External debt profiles** including short-term and long-term borrowing
    - **Trade performance**, export/import ratios, and reserve positions
    - **Social indicators** like population growth, education, and life expectancy
    - **Environmental and energy statistics**

    📊 Select an indicator and a preferred chart type below to begin exploring over six decades of Sri Lanka’s progress and challenges.
    """)



# Function to load and preprocess the dataset
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path, na_values='..')
        id_vars = ["Country Name", "Country Code", "Series Name", "Series Code"]
        year_cols = [col for col in df.columns if col.startswith("19") or col.startswith("20")]

        # Melt into long format
        df_long = pd.melt(df, id_vars=id_vars, value_vars=year_cols,
                          var_name="Year", value_name="Value")

        df_long["Year"] = df_long["Year"].str.extract(r"(\d{4})").astype(int)
        df_long.rename(columns={"Series Name": "Indicator Name"}, inplace=True)
        df_long.dropna(subset=["Value"], inplace=True)
        df_long["Value"] = pd.to_numeric(df_long["Value"], errors='coerce')

        return df_long
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

# Function to convert DataFrame to CSV for download
@st.cache_data
def convert_df_to_csv(df_to_convert):
    try:
        if df_to_convert.empty:
            st.warning("The DataFrame is empty. Nothing to download.")
            return b""
        return df_to_convert.to_csv(index=False).encode("utf-8")
    except Exception as e:
        st.error(f"Failed to convert DataFrame to CSV: {e}")
        return b""

# Key indicators list
KEY_INDICATORS = [
    "GDP (current US$)",
    "GDP growth (annual %)",
    "GNI per capita, Atlas method (current US$)",
    "Inflation, consumer prices (annual %)",
    "Population, total",
    "Life expectancy at birth, total (years)",
    "External debt stocks, total (DOD, current US$)",
    "Total debt service (% of exports of goods, services and primary income)",
    "Exports of goods and services (% of GDP)",
    "Imports of goods and services (% of GDP)",
    "Foreign direct investment, net inflows (BoP, current US$)",
    "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)",
    "Unemployment, total (% of total labor force) (modeled ILO estimate)",
    "Agriculture, forestry, and fishing, value added (% of GDP)"
]

# Load dataset
file_name = "preprocessed_dataset.csv"
df = load_data(file_name)

# Validate and filter
if df.empty or "Indicator Name" not in df.columns:
    st.error("The dataset is empty or incorrectly formatted. Please check the file.")
    st.stop()

# Filter for selected indicators
df = df[df["Indicator Name"].isin(KEY_INDICATORS)]
if df.empty:
    st.error("No data available for selected indicators.")
    st.stop()

# Sidebar selection
indicator_selected = st.sidebar.selectbox("Select an Indicator", sorted(df["Indicator Name"].unique()))
chart_type = st.sidebar.selectbox("Select Chart Type", ["Line Chart", "Area Chart", "Bar Chart", "Box Plot", "Pie Chart"])

# Filtered data for selected indicator
df_selected = df[df["Indicator Name"] == indicator_selected].copy()

# Chart rendering
st.markdown(f"### {indicator_selected}")

if chart_type == "Line Chart":
    fig = px.line(df_selected, x="Year", y="Value", title=indicator_selected)
elif chart_type == "Area Chart":
    fig = px.area(df_selected, x="Year", y="Value", title=indicator_selected)
elif chart_type == "Bar Chart":
    fig = px.bar(df_selected, x="Year", y="Value", title=indicator_selected)
elif chart_type == "Box Plot":
    fig = px.box(df_selected, x="Year", y="Value", title=indicator_selected)
elif chart_type == "Pie Chart":
    pie_df = df_selected[df_selected['Year'] == df_selected['Year'].max()]
    fig = px.pie(pie_df, names="Indicator Name", values="Value", title=f"{indicator_selected} - {pie_df['Year'].values[0]}")
else:
    fig = px.line(df_selected, x="Year", y="Value", title=indicator_selected)

st.plotly_chart(fig, use_container_width=True)

# --- CSV Download ---
st.markdown("---")
csv_data = convert_df_to_csv(df_selected[["Year", "Indicator Name", "Series Code", "Value"]])
safe_file_name = "".join([c if c.isalnum() else "_" for c in indicator_selected])[:50]
csv_filename = f"{safe_file_name}_data.csv"

st.download_button(
    label="\U0001F4E5 Download Data as CSV",
    data=csv_data,
    file_name=csv_filename,
    mime="text/csv"
)

