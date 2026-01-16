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
st.subheader("Data Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{len(cleaned_chlamydia):,}")
col2.metric("States", cleaned_chlamydia["Geography"].nunique())
col3.metric("Years", f'{cleaned_chlamydia["Year"].min()} - {cleaned_chlamydia["Year"].max()}')


st.header("Charts", divider="red")

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

#----------------------------------DARK MODE TOGGLE----------------------------------

# Dark mode toggle
dark_mode = st.toggle("Chart Dark Mode")

if dark_mode:
    bg_color = "#262730"
    bar_color = "#3c3d4d"
    txt_color = "white"     
else:
    bg_color = "white"            
    txt_color = "black"           
    bar_color = "red"             

#----------------------------------CHARTS----------------------------------

#----------------Cases Over Time Chart----------------
st.subheader("Total Cases Over Time")

# Aggregate cases by year
yearly_cases = chlamydia_filtered.groupby("Year")["Cases"].sum().reset_index()

left_col, right_col = st.columns([2,1])

with left_col:
    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=txt_color)

    yearly_cases.plot(x="Year", y="Cases", kind="line", ax=ax, color="#e6550d")
    ax.set_xlabel("Year", color=txt_color)
    ax.set_ylabel("Cases", rotation=0, labelpad=30, color=txt_color)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    plt.tight_layout()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig, use_container_width=False)

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
with right_col:
    st.write(f''' 
            **Key Insights:**
            - Total cases in {yearly_cases["Year"].min()}: {first_year_cases:,}
            - Total cases in {yearly_cases["Year"].max()}: {last_year_cases:,}
            - Overall trend: {trend}
            ''')

st.markdown("---")

#----------------Top 10 States Chart----------------

# Calculate state totals
top_states = chlamydia_filtered.groupby("Geography")["Cases"].sum().sort_values(ascending=False).head(10).reset_index()

top_states = top_states.rename(columns={"Geography": "State"})

left_col, right_col = st.columns([1.5,1])

with left_col:
    st.subheader("Top States with the Highest Cases")
    # Create horizontal bar chart
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    fig2.patch.set_facecolor(bg_color)
    ax2.set_facecolor(bg_color)
    ax2.tick_params(colors=txt_color)


    ax2.barh(top_states["State"], top_states["Cases"], color="#e6550d")
    ax2.set_xlabel("Total Cases", fontsize=12, color=txt_color)
    ax2.set_ylabel("States", rotation=0, fontsize=12, color=txt_color)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    ax2.invert_yaxis()
    plt.tight_layout()

    st.pyplot(fig2, use_container_width=False)

with right_col:
    # Showing the actual numbers
    st.subheader("Data")
    st.dataframe(top_states.style.format({"Cases": "{:,.0f}"}), hide_index=True)

st.markdown("---")

#----------------Top 10 States (All Time Rate per 100000)----------------

top_states_rate = chlamydia_filtered.groupby("Geography")["Rate per 100000"].sum().sort_values(ascending=False).head(10).reset_index()

top_states_rate = top_states_rate.rename(columns={
    "Geography": "State",
    "Rate per 100000": "Rate per 100,000"
})

left_col, right_col = st.columns([1.5,1])

with left_col:
    st.subheader("Top States with the Highest Cases (Rate per 100,000)")
    fig3, ax3 = plt.subplots(figsize=(10, 6))

    fig3.patch.set_facecolor(bg_color)
    ax3.set_facecolor(bg_color)
    ax3.tick_params(colors=txt_color)

    ax3.barh(top_states_rate["State"], top_states_rate["Rate per 100,000"], color="#3182bd")
    ax3.set_xlabel("Rate Per 100,000", color=txt_color)
    ax3.set_ylabel("States", rotation=0, labelpad=10, color=txt_color)
    ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    ax3.invert_yaxis()
    plt.tight_layout()

    st.pyplot(fig3, use_container_width=False)

with right_col:
# Showing the actual numbers
    st.subheader("Data")
    st.dataframe(top_states_rate.style.format({"Rate per 100,000": "{:,.0f}"}), hide_index=True)

st.markdown("---")

#----------------State Comparison Over Time----------------
st.subheader("State Comparison of Cases Over Time")
state_comparison = chlamydia_filtered[chlamydia_filtered["Geography"].isin(selected_states)]
state_yearly = state_comparison.groupby(["Year", "Geography"])["Cases"].sum().reset_index()

col1, col2 = st.columns([10,1])

with col1:
    fig4, ax4 = plt.subplots(figsize=(12, 6))

    fig4.patch.set_facecolor(bg_color)
    ax4.set_facecolor(bg_color)
    ax4.tick_params(colors=txt_color)

    for state in selected_states:
        state_data = state_yearly[state_yearly["Geography"] == state]
        ax4.plot(state_data["Year"], state_data["Cases"], marker="o", label=state)
    ax4.set_xlabel("Year", color=txt_color)
    ax4.set_ylabel("Cases", labelpad=30, rotation=0, color=txt_color)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    plt.tight_layout()
    st.pyplot(fig4, use_container_width=False)

st.markdown("---")

#----------------------------------Interactive Map----------------------------------
st.subheader("Map Distribution")

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
    title=f"Cases by State for {latest_year} (Rate Per 100,000) ",
    color_continuous_scale="Oranges",
    labels={"Rate per 100000": "Rate Per 100,000"}
)

fig_map.update_layout(
    geo=dict(bgcolor=bg_color),
    margin=dict(r=0, l=0, t=25, b=0),
    width=400,
    height=600
    )

st.plotly_chart(fig_map)

st.markdown("---")
