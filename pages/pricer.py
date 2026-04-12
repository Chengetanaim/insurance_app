import streamlit as st
import plotly.graph_objects as go
import json
from utils.pricing import price_policy, get_factor_options, get_risk_category, BASE_RATES
from utils.auth import save_quote, get_current_user


PRODUCT_ICONS = {"Motor": "🚗", "Life": "❤️", "Property": "🏠", "Health": "🏥"}
PRODUCT_DESCRIPTIONS = {
    "Motor":    "Private, commercial, or hire vehicle comprehensive pricing using driver and vehicle risk factors.",
    "Life":     "Term life insurance premium calculation incorporating age, lifestyle, and sum assured.",
    "Property": "Commercial and residential property cover rated on construction, security, and location.",
    "Health":   "Medical aid fund pricing accounting for age, plan tier, and pre-existing conditions.",
}


def show_pricer():
    st.markdown("## 💰 Price a Policy")
    st.markdown("Select a product and complete the rating factors below.")
    st.markdown("---")

    user = get_current_user()

    # ── Product selection ─────────────────────────────────────────────────────
    product = st.selectbox(
        "Insurance Product",
        list(BASE_RATES.keys()),
        format_func=lambda p: f"{PRODUCT_ICONS[p]}  {p} Insurance",
    )

    st.markdown(f"""
    <div class='iq-card' style='margin:0.5rem 0 1.2rem 0;'>
        <span style='font-size:0.85rem; color:#8899bb;'>{PRODUCT_DESCRIPTIONS[product]}</span>
        <br><span style='color:#0fd6c2; font-family:Syne,sans-serif; font-weight:700;'>
        Base Rate: ${BASE_RATES[product]:,.0f} p.a.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Insured details ───────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        insured_name = st.text_input("Insured Name / Reference", placeholder="e.g. Tinashe Moyo")
    with col_b:
        cover_amount = st.number_input(
            "Sum Insured / Cover Amount (USD)",
            min_value=0, max_value=10_000_000,
            value=100_000 if product == "Property" else 50_000,
            step=10_000,
        )

    st.markdown("---")
    st.markdown("### Rating Factors")

    factors = get_factor_options(product)
    selections = {"cover_amount": cover_amount}

    cols = st.columns(2)
    for i, (factor_key, options) in enumerate(factors.items()):
        label = factor_key.replace("_", " ").title()
        with cols[i % 2]:
            chosen = st.selectbox(label, list(options.keys()), key=f"factor_{product}_{factor_key}")
            selections[factor_key] = chosen

    st.markdown("---")

    # ── Calculate ─────────────────────────────────────────────────────────────
    if st.button("⚡  Calculate Premium", use_container_width=False):
        result = price_policy(product, selections)
        st.session_state["last_result"] = result
        st.session_state["last_product"] = product
        st.session_state["last_insured"] = insured_name
        st.session_state["last_selections"] = selections

    if "last_result" in st.session_state and st.session_state.get("last_product") == product:
        result = st.session_state["last_result"]
        risk_label, risk_color = get_risk_category(result["risk_score"])

        st.markdown("### 📋 Pricing Result")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Annual Premium", f"${result['premium']:,.2f}")
        m2.metric("Monthly Premium", f"${result['premium']/12:,.2f}")
        m3.metric("Risk Score", f"{result['risk_score']:.1f} / 100")
        m4.metric("Composite Factor", f"×{result['composite_factor']:.4f}")

        st.markdown(f"""
        <div style='margin: 0.5rem 0; font-size:0.85rem;'>
            Risk Category: <span style='color:{risk_color}; font-weight:700;
            font-family:Syne,sans-serif;'>{risk_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Factor waterfall chart
        col_chart, col_table = st.columns([3, 2])
        with col_chart:
            st.markdown("**Premium Build-up (Waterfall)**")
            labels = [b[0] for b in result["breakdown"]]
            values = [result["breakdown"][0][1]] + [
                result["breakdown"][i][1] - result["breakdown"][i-1][1]
                for i in range(1, len(result["breakdown"]))
            ]
            colors = ["#0fd6c2"] + ["#22c55e" if v >= 0 else "#ef4444" for v in values[1:]]

            fig = go.Figure(go.Bar(
                x=labels, y=values,
                marker_color=colors,
                text=[f"${v:,.0f}" for v in values],
                textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2eaf6", yaxis_title="USD",
                margin=dict(t=20, b=40, l=10, r=10),
                xaxis_tickangle=-25,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("**Factor Details**")
            for fname, chosen, fval in result["factor_details"]:
                delta_str = f"+{(fval-1)*100:.0f}%" if fval > 1 else f"{(fval-1)*100:.0f}%"
                color = "#ef4444" if fval > 1.15 else "#22c55e" if fval < 0.95 else "#8899bb"
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:4px 0;
                     border-bottom:1px solid rgba(15,214,194,0.1); font-size:0.82rem;'>
                    <span style='color:#8899bb;'>{fname}</span>
                    <span>{chosen}</span>
                    <span style='color:{color}; font-weight:700;'>{delta_str}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── Save quote ────────────────────────────────────────────────────────
        st.markdown("---")
        col_save, col_clear = st.columns([2, 1])
        with col_save:
            if st.button("💾  Save Quote", use_container_width=True):
                qid = save_quote(
                    user["id"],
                    product,
                    insured_name or "Unnamed",
                    result["premium"],
                    result["risk_score"],
                    json.dumps(selections, default=str),
                )
                st.success(f"Quote #{qid} saved successfully! View it in My Quotes.")
        with col_clear:
            if st.button("🗑️  Clear", use_container_width=True):
                st.session_state.pop("last_result", None)
                st.rerun()
