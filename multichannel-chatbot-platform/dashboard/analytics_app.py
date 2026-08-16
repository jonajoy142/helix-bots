"""
Streamlit analytics dashboard reading straight from the shared platform.db.

Run:
    streamlit run dashboard/analytics_app.py

Shows exactly the kind of metrics a WhatsApp automation platform's customers
care about: message volume by channel, escalation rate, and recent
conversations.
"""
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.config import settings

st.set_page_config(page_title="Helix-style Bot Analytics", layout="wide")


@st.cache_data(ttl=5)
def load_data():
    conn = sqlite3.connect(settings.DB_PATH)
    df = pd.read_sql_query("SELECT * FROM conversations ORDER BY created_at DESC", conn)
    conn.close()
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
    return df


st.title("🤖 Multi-Channel Bot Analytics")
st.caption("Live view of conversations flowing through the shared LangGraph agent, across web + WhatsApp.")

df = load_data()

if df.empty:
    st.info("No conversations yet. Send a few messages via the widget or WhatsApp webhook, then refresh.")
else:
    col1, col2, col3, col4 = st.columns(4)
    total_msgs = len(df)
    unique_users = df["user_id"].nunique()
    escalation_rate = round(100 * df["escalated"].sum() / max(len(df[df.role == "bot"]), 1), 1)
    channels = df["channel"].nunique()

    col1.metric("Total messages", total_msgs)
    col2.metric("Unique users", unique_users)
    col3.metric("Escalation rate", f"{escalation_rate}%")
    col4.metric("Active channels", channels)

    st.subheader("Messages by channel")
    channel_counts = df.groupby("channel").size().reset_index(name="messages")
    st.plotly_chart(px.bar(channel_counts, x="channel", y="messages", color="channel"), use_container_width=True)

    st.subheader("Message volume over time")
    df["date"] = df["created_at"].dt.date
    daily = df.groupby(["date", "channel"]).size().reset_index(name="messages")
    st.plotly_chart(px.line(daily, x="date", y="messages", color="channel", markers=True), use_container_width=True)

    st.subheader("Recent conversations")
    st.dataframe(
        df[["created_at", "channel", "user_id", "role", "message", "escalated"]].head(50),
        use_container_width=True,
        hide_index=True,
    )
