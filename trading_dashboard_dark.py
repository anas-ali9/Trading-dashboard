import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =====================
# Load Data
# =====================
df = pd.read_excel("trades_database.xlsx")

# =====================
# Pre-computed Metrics
# =====================
df["Running_Max"] = df["Balance_After"].cummax()
df["Drawdown"] = df["Balance_After"] - df["Running_Max"]

df["Cumulative_Wins"] = (df["Result"] == "WIN").cumsum()
df["Running_Winrate"] = df["Cumulative_Wins"] / (df.index + 1) * 100

# =====================
# Page Configuration
# =====================
st.set_page_config(
    page_title="Trading Dashboard",
    layout="wide"
)

# Dark background styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Trading Performance Dashboard")

# =====================
# Sidebar Filters
# =====================
st.sidebar.header("Filters")

selected_markets = st.sidebar.multiselect(
    "Select Markets",
    options=df["Market"].unique(),
    default=df["Market"].unique()
)

result_filter = st.sidebar.selectbox(
    "Trade Result",
    ["All", "WIN", "LOSS"]
)

filtered_df = df[df["Market"].isin(selected_markets)]

if result_filter != "All":
    filtered_df = filtered_df[filtered_df["Result"] == result_filter]

# =====================
# Key Metrics
# =====================
st.subheader("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Trades", len(filtered_df))
col2.metric("Winrate (%)", round((filtered_df["Result"] == "WIN").mean() * 100, 2))
col3.metric("Final Balance", round(filtered_df["Balance_After"].iloc[-1], 2))
col4.metric("Most Traded Market", filtered_df["Market"].value_counts().idxmax())
col5.metric("Max Drawdown", round(filtered_df["Drawdown"].min(), 2))

st.markdown("---")

# =====================
# Plot Settings
# =====================
plt.style.use("dark_background")

# =====================
# Equity Curve
# =====================
st.subheader("Equity Curve")

fig, ax = plt.subplots()
ax.plot(filtered_df["Balance_After"], color="cyan")
ax.set_xlabel("Trade Number")
ax.set_ylabel("Account Balance")
st.pyplot(fig)

# =====================
# Running Winrate
# =====================
st.subheader("Running Winrate")

fig, ax = plt.subplots()
ax.plot(filtered_df["Running_Winrate"], color="gold")
ax.set_xlabel("Trade Number")
ax.set_ylabel("Winrate (%)")
ax.set_ylim(0, 100)
st.pyplot(fig)

# =====================
# Trades Per Market
# =====================
st.subheader("Trades Per Market")

fig, ax = plt.subplots()
filtered_df["Market"].value_counts().plot(
    kind="bar",
    color="gray",
    ax=ax
)
ax.set_ylabel("Number of Trades")
st.pyplot(fig)

# =====================
# Winrate Per Market
# =====================
st.subheader("Winrate Per Market")

winrate_per_market = (
    filtered_df.groupby("Market")["Result"]
    .apply(lambda x: (x == "WIN").mean() * 100)
)

fig, ax = plt.subplots()
winrate_per_market.plot(
    kind="bar",
    color="lightgray",
    ax=ax
)
ax.set_ylabel("Winrate (%)")
ax.set_ylim(0, 100)
st.pyplot(fig)

# =====================
# Market Distribution (Minimal Colors)
# =====================
st.subheader("Market Distribution")

minimal_colors = ["#2c2c2c", "#4a4a4a", "#6a6a6a", "#8a8a8a"]

fig, ax = plt.subplots()
filtered_df["Market"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%",
    colors=minimal_colors,
    ylabel="",
    ax=ax
)
st.pyplot(fig)
