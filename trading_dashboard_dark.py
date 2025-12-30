import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================
# Load Data
# =====================
df = pd.read_excel("trades_database.xlsx")

# =====================
# Compute Metrics
# =====================
df["Running_Max"] = df["Balance_After"].cummax()
df["Drawdown"] = df["Balance_After"] - df["Running_Max"]
df["Cumulative_Wins"] = (df["Result"] == "WIN").cumsum()
df["Running_Winrate"] = df["Cumulative_Wins"] / (df.index + 1) * 100

# =====================
# Page Config & Styling
# =====================
st.set_page_config(page_title="Trading Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stSidebar { background-color: #11151f; }
    .stMarkdown, .stText, .stSubheader { color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Trading Dashboard")

# =====================
# Sidebar Filters
# =====================
st.sidebar.header("Filters")
selected_markets = st.sidebar.multiselect(
    "Select Markets",
    options=df["Market"].unique(),
    default=df["Market"].unique()
)
result_filter = st.sidebar.selectbox("Trade Result", ["All", "WIN", "LOSS"])

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
# Equity Curve
# =====================
st.subheader("Equity Curve")
fig = go.Figure()
fig.add_trace(go.Scatter(
    y=filtered_df["Balance_After"],
    mode="lines+markers",
    name="Equity",
    line=dict(color="cyan")
))
fig.update_layout(
    template="plotly_dark",
    xaxis_title="Trade Number",
    yaxis_title="Account Balance ($)"
)
st.plotly_chart(fig, width='stretch')

# =====================
# Running Winrate
# =====================
st.subheader("Running Winrate (%)")
fig = go.Figure()
fig.add_trace(go.Scatter(
    y=filtered_df["Running_Winrate"],
    mode="lines+markers",
    name="Winrate",
    line=dict(color="gold")
))
fig.update_layout(
    template="plotly_dark",
    xaxis_title="Trade Number",
    yaxis_title="Winrate (%)",
    yaxis=dict(range=[0, 100])
)
st.plotly_chart(fig, width='stretch')

# =====================
# Trades per Market
# =====================
st.subheader("Trades per Market")
trade_counts = filtered_df["Market"].value_counts().reset_index()
trade_counts.columns = ["Market", "Trades"]

fig = px.bar(
    trade_counts,
    x="Market",
    y="Trades",
    color="Market",
    color_discrete_sequence=px.colors.sequential.Greys,
    template="plotly_dark"
)
st.plotly_chart(fig, width='stretch')

# =====================
# Winrate per Market
# =====================
st.subheader("Winrate per Market (%)")
winrate_per_market = filtered_df.groupby("Market")["Result"].apply(lambda x: (x=="WIN").mean()*100).reset_index()
winrate_per_market.columns = ["Market", "Winrate"]

fig = px.bar(
    winrate_per_market,
    x="Market",
    y="Winrate",
    color="Market",
    color_discrete_sequence=px.colors.sequential.Greys,
    template="plotly_dark",
    range_y=[0,100]
)
st.plotly_chart(fig, width='stretch')

# =====================
# Market Distribution
# =====================
st.subheader("Market Distribution")
market_counts = filtered_df["Market"].value_counts().reset_index()
market_counts.columns = ["Market", "Trades"]

fig = px.pie(
    market_counts,
    names="Market",
    values="Trades",
    color_discrete_sequence=px.colors.sequential.Greys,
    template="plotly_dark"
)
st.plotly_chart(fig, width='stretch')
