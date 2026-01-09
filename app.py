import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# Page config
st.set_page_config(page_title="STD Dashboard", page_icon="📊", layout="wide")

# Title 
st.title("📊 U.S. Chlamydia Cases Dashboard")
st.write("Analyzing CDC data on Chlamydia cases across U.S. states (2000-2023)")

# Loading cleaned data
cleaned_chlamydia = pd.read_csv("data/cleaned/CHLAMYDIA_CLEANED.csv")
cleaned_chlamydia = cleaned_chlamydia.iloc[:, 1:]

# Showing basic info
st.subheader("Dataset Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{len(cleaned_chlamydia):,}")
col2.metric("States", cleaned_chlamydia["Geography"].nunique())
col3.metric("Years", f'{cleaned_chlamydia["Year"].min()} - {cleaned_chlamydia["Year"].max()}')

# Showing the data
st.subheader("Raw Data Sample")
st.dataframe(cleaned_chlamydia.head(10), hide_index=True)

st.success("Dashboard is running!")


#----------------------------------SIDEBAR FILTER----------------------------------

# Sidebar Filter
st.sidebar.header("Filters")
st.sidebar.write("Use these filters to explore the data!")

# Year range selector
min_year = int(cleaned_chlamydia["Year"].min())
max_year = int(cleaned_chlamydia["Year"].max())

year_range = st.sidebar.slider(
    "Select the year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# dataframe filter based on selection
chlamydia_filtered = cleaned_chlamydia[(cleaned_chlamydia["Year"] >= year_range[0]) & (cleaned_chlamydia["Year"] <= year_range[1])]

st.sidebar.success(f"Showing data from {year_range[0]} to {year_range[1]}")

# Comparing Specific States
st.sidebar.subheader("Compare Specific States")
selected_states = st.sidebar.multiselect(
    "Choose states to compare",
    options=sorted(cleaned_chlamydia["Geography"].unique()),
    default=["California", "Texas", "Florida"]
)

#----------------------------------CHARTS----------------------------------

#----------------Cases Over Time Chart----------------
st.subheader("Chlamydia Cases Over Time")

# Aggregate cases by year
yearly_cases = chlamydia_filtered.groupby("Year")["Cases"].sum().reset_index()

# Create the chart
fig, ax = plt.subplots(figsize=(10, 6))
yearly_cases.plot(x="Year", y="Cases", kind="line", ax=ax, title="Cases Over Time")
ax.set_xlabel("Year")
ax.set_ylabel("Cases", rotation=0, labelpad=30)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
plt.tight_layout()

st.pyplot(fig)

first_year_cases = int(yearly_cases["Cases"].iloc[0])
last_year_cases = int(yearly_cases["Cases"].iloc[-1])

# Compare them and decide the trend
if last_year_cases > first_year_cases:
    trend = "Increasing"
elif last_year_cases < first_year_cases:
    trend = "Decreasing"
else:
    trend = "Stable"

# Context
st.write(f''' 
        **Key Insights:**
        - Total cases in {yearly_cases["Year"].min()}: {first_year_cases:,}
        - Total cases in {yearly_cases["Year"].max()}: {last_year_cases:,}
        - Overall trend: {trend}
        ''')

#----------------Top 10 States Chart----------------
st.subheader("Top 10 States by Total Cases")

# Calculate state totals
top_states = chlamydia_filtered.groupby("Geography")["Cases"].sum().sort_values(ascending=False).head(10).reset_index()

# Create horizontal bar chart
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.barh(top_states["Geography"], top_states["Cases"], color="coral")
ax2.set_title("States with Highest Chlamydia Case Counts")
ax2.set_xlabel("Total Cases", fontsize=12)
ax2.set_ylabel("States", rotation=0, fontsize=12)
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
ax2.invert_yaxis()
plt.tight_layout()

st.pyplot(fig2)

# Showing the actual numbers
st.write("**The Data:**")
st.dataframe(top_states.style.format({"Cases": "{:,.0f}"})) # formatting the cases column

#----------------Top 10 States (All Time Rate per 100000)----------------
top_states_rate = chlamydia_filtered.groupby("Geography")["Rate per 100000"].sum().sort_values(ascending=False).head(10).reset_index()

fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.barh(top_states_rate["Geography"], top_states_rate["Rate per 100000"], color="red")
ax3.set_title("Top 10 States (All Time Rate per 100,000)")
ax3.set_xlabel("Rate Per 100,000")
ax3.set_ylabel("States", rotation=0, labelpad=10)
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
ax3.invert_yaxis()
plt.tight_layout()

st.pyplot(fig3)

# Showing the actual numbers
st.write("**The Data:**")
st.dataframe(top_states_rate.style.format({"Rate per 100000": "{:,.0f}"}))

#----------------State Comparison Over Time----------------
st.subheader("State Comparison Over Time")
state_comparison = chlamydia_filtered[chlamydia_filtered["Geography"].isin(selected_states)]
state_yearly = state_comparison.groupby(["Year", "Geography"])["Cases"].sum().reset_index()

fig4, ax4 = plt.subplots(figsize=(12, 6))
for state in selected_states:
    state_data = state_yearly[state_yearly["Geography"] == state]
    ax4.plot(state_data["Year"], state_data["Cases"], marker="o", label=state)
ax4.set_xlabel("Year")
ax4.set_ylabel("Cases")
ax4.set_title("Cases by State Over Time")
ax4.legend()
ax4.grid(True, alpha=0.3)
plt.tight_layout()

st.pyplot(fig4)


#----------------------------------Interactive Map----------------------------------
st.subheader("Geographic Distribution")

state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}


latest_year = chlamydia_filtered["Year"].max()
map_data = chlamydia_filtered[chlamydia_filtered["Year"] == latest_year].copy()
map_data["state_abbrev"] = map_data["Geography"].map(state_abbreviations)

fig_map = px.choropleth(
    map_data,
    locations="state_abbrev",
    locationmode="USA-states",
    color="Rate per 100000",
    scope="usa",
    title=f"Chlamydia Cases Per 100,000 by State ({latest_year})",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_map, use_container_width=True)
