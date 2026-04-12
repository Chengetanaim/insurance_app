import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.pricing import (
    price_policy, get_factor_options, sensitivity_analysis,
    BASE_RATES, ALL_FACTORS, get_risk_category,
)


def show_risk_explorer():
    st.markdown("## 🔍 Risk Explorer")
    st.markdown("Analyse how individual rating factors drive premium and risk score.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🎛️  Sensitivity Analysis", "🗺️  Factor Heatmap", "📐  Portfolio Simulator"])

    # ── Tab 1: Sensitivity ────────────────────────────────────────────────────
    with tab1:
        st.markdown("**See how changing one factor shifts the premium while keeping others fixed.**")
        col1, col2 = st.columns(2)
        with col1:
            product = st.selectbox("Product", list(BASE_RATES.keys()), key="se_prod")
        with col2:
            factor_keys = list(ALL_FACTORS[product].keys())
            vary_factor = st.selectbox(
                "Factor to Vary",
                factor_keys,
                format_func=lambda x: x.replace("_", " ").title(),
                key="se_factor",
            )

        st.markdown("**Fix all other factors:**")
        base_selections = {}
        cols = st.columns(3)
        for i, fk in enumerate(factor_keys):
            if fk != vary_factor:
                opts = list(ALL_FACTORS[product][fk].keys())
                with cols[i % 3]:
                    base_selections[fk] = st.selectbox(
                        fk.replace("_", " ").title(), opts, key=f"se_fix_{fk}"
                    )

        results = sensitivity_analysis(product, base_selections, vary_factor)
        df = pd.DataFrame(results)

        fig = go.Figure()
        fig.add_bar(
            x=df["option"], y=df["premium"],
            marker_color=["#0fd6c2" if r < df["premium"].mean() else "#f5a623" for r in df["premium"]],
            text=[f"${p:,.0f}" for p in df["premium"]],
            textposition="outside",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2eaf6", title=f"Premium by {vary_factor.replace('_',' ').title()}",
            yaxis_title="Annual Premium (USD)", margin=dict(t=40, b=60, l=10, r=10),
            xaxis_tickangle=-20,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Risk score companion
        fig2 = px.line(
            df, x="option", y="risk_score",
            markers=True, color_discrete_sequence=["#f5a623"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2eaf6", title="Risk Score by Option",
            yaxis_title="Risk Score (0-100)", margin=dict(t=40, b=60, l=10, r=10),
            xaxis_tickangle=-20,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Factor Heatmap ─────────────────────────────────────────────────
    with tab2:
        st.markdown("**Compare premium impact of every factor value across all products.**")
        prod_h = st.selectbox("Product", list(BASE_RATES.keys()), key="hm_prod")
        factors_h = ALL_FACTORS[prod_h]

        heat_data = []
        for fk, opts in factors_h.items():
            for option, fval in opts.items():
                heat_data.append({
                    "Factor": fk.replace("_", " ").title(),
                    "Option": option,
                    "Multiplier": fval,
                    "Premium Impact": f"×{fval:.2f}",
                })

        df_h = pd.DataFrame(heat_data)
        pivot = df_h.pivot(index="Option", columns="Factor", values="Multiplier").fillna(0)

        fig3 = px.imshow(
            pivot,
            color_continuous_scale=["#0b1629", "#0fd6c2", "#f5a623", "#ef4444"],
            aspect="auto",
            text_auto=".2f",
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2eaf6", margin=dict(t=30, b=10, l=10, r=10),
            coloraxis_colorbar=dict(title="×Factor"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Tab 3: Portfolio Simulator ────────────────────────────────────────────
    with tab3:
        st.markdown("**Simulate a portfolio of N policies and analyse its distribution.**")
        import numpy as np

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            prod_sim = st.selectbox("Product", list(BASE_RATES.keys()), key="sim_prod")
        with col_s2:
            n_policies = st.slider("Number of Policies", 10, 500, 100)
        with col_s3:
            seed = st.number_input("Random Seed", value=42)

        if st.button("▶️  Run Simulation"):
            np.random.seed(int(seed))
            facs = ALL_FACTORS[prod_sim]
            records = []
            for _ in range(n_policies):
                sel = {}
                for fk, opts in facs.items():
                    sel[fk] = np.random.choice(list(opts.keys()))
                res = price_policy(prod_sim, sel)
                rl, rc = get_risk_category(res["risk_score"])
                records.append({"premium": res["premium"], "risk_score": res["risk_score"], "risk_cat": rl})

            sim_df = pd.DataFrame(records)
            total = sim_df["premium"].sum()
            mean  = sim_df["premium"].mean()
            p95   = sim_df["premium"].quantile(0.95)

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Total Portfolio Premium", f"${total:,.0f}")
            mc2.metric("Mean Policy Premium",     f"${mean:,.0f}")
            mc3.metric("95th Percentile",         f"${p95:,.0f}")
            mc4.metric("Loss Ratio Proxy",        f"{(mean/BASE_RATES[prod_sim]*100):.1f}%")

            fig4 = px.histogram(sim_df, x="premium", nbins=30, color="risk_cat",
                                color_discrete_map={
                                    "Low Risk":"#22c55e","Moderate Risk":"#f59e0b",
                                    "High Risk":"#f97316","Very High Risk":"#ef4444"
                                })
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2eaf6", title="Simulated Portfolio Premium Distribution",
                margin=dict(t=40, b=30, l=10, r=10),
            )
            st.plotly_chart(fig4, use_container_width=True)
