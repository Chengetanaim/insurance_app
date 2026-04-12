import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.auth import get_user_quotes, get_all_quotes_stats, get_current_user


def show_dashboard():
    user = get_current_user()
    st.markdown(f"## 👋 Welcome back, {user['full_name'] or user['username']}")
    st.markdown("Here's your actuarial workspace overview.")
    st.markdown("---")

    quotes = get_user_quotes(user["id"])

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    total_quotes = len(quotes)
    total_premium = sum(q[3] for q in quotes if q[3]) if quotes else 0
    avg_risk = (sum(q[4] for q in quotes if q[4]) / total_quotes) if total_quotes else 0
    products_used = len(set(q[1] for q in quotes)) if quotes else 0

    c1.metric("Total Quotes", total_quotes)
    c2.metric("Total Premium Value", f"${total_premium:,.0f}")
    c3.metric("Avg Risk Score", f"{avg_risk:.1f} / 100")
    c4.metric("Products Used", f"{products_used} / 4")

    st.markdown("---")

    if not quotes:
        st.info("🧭 You haven't generated any quotes yet. Head to **Price a Policy** to get started!")
        return

    df = pd.DataFrame(quotes, columns=["id","product","insured","premium","risk_score","created_at","status"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    col_left, col_right = st.columns(2)

    # ── Premium by product ────────────────────────────────────────────────────
    with col_left:
        st.markdown("#### Premium Distribution by Product")
        prod_grp = df.groupby("product")["premium"].sum().reset_index()
        fig = px.pie(
            prod_grp, names="product", values="premium",
            color_discrete_sequence=["#0fd6c2","#f5a623","#8b5cf6","#ef4444"],
            hole=0.55,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2eaf6", showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Risk score distribution ───────────────────────────────────────────────
    with col_right:
        st.markdown("#### Risk Score Distribution")
        fig2 = px.histogram(
            df, x="risk_score", nbins=10,
            color_discrete_sequence=["#0fd6c2"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2eaf6", xaxis_title="Risk Score",
            yaxis_title="Count", margin=dict(t=10, b=30, l=10, r=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Recent quotes table ───────────────────────────────────────────────────
    st.markdown("#### Recent Quotes")
    recent = df.sort_values("created_at", ascending=False).head(5)
    display = recent[["product","insured","premium","risk_score","created_at"]].copy()
    display.columns = ["Product","Insured Name","Premium ($)","Risk Score","Date"]
    display["Premium ($)"] = display["Premium ($)"].apply(lambda x: f"${x:,.2f}")
    display["Date"] = display["Date"].dt.strftime("%d %b %Y %H:%M")
    st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Global stats ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Platform-wide Statistics (All Users)")
    stats = get_all_quotes_stats()
    if stats:
        sdf = pd.DataFrame(stats, columns=["Product","Quote Count","Avg Premium","Min Premium","Max Premium"])
        sdf["Avg Premium"] = sdf["Avg Premium"].apply(lambda x: f"${x:,.2f}" if x else "—")
        sdf["Min Premium"] = sdf["Min Premium"].apply(lambda x: f"${x:,.2f}" if x else "—")
        sdf["Max Premium"] = sdf["Max Premium"].apply(lambda x: f"${x:,.2f}" if x else "—")
        st.dataframe(sdf, use_container_width=True, hide_index=True)
