import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

# Cases Over Time Chart
st.subheader("Chlamydia Cases Over Time")

# Aggregate cases by year
yearly_cases = cleaned_chlamydia.groupby("Year")["Cases"].sum().reset_index()

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


# Top 10 States Chart
st.subheader("Top 10 States by Total Cases")

# Calculate state totals
top_states = cleaned_chlamydia.groupby("Geography")["Cases"].sum().sort_values(ascending=False).head(10).reset_index()

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

# Show the actual numbers
st.write("**Detailed Numbers:**")
st.dataframe(top_states.style.format({"Cases": "{:,.0f}"})) # formatting the cases column