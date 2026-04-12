import streamlit as st
import pandas as pd
import json
from utils.auth import get_user_quotes, delete_quote, get_current_user
from utils.pricing import get_risk_category


def show_quotes():
    st.markdown("## 📁 My Quotes")
    st.markdown("Manage and review all your saved policy quotes.")
    st.markdown("---")

    user = get_current_user()
    quotes = get_user_quotes(user["id"])

    if not quotes:
        st.info("No quotes yet. Head to **Price a Policy** to generate your first quote!")
        return

    df = pd.DataFrame(quotes, columns=["id","product","insured","premium","risk_score","created_at","status"])

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        prod_filter = st.multiselect("Filter by Product", df["product"].unique().tolist(),
                                      default=df["product"].unique().tolist())
    with col_f2:
        min_p, max_p = float(df["premium"].min()), float(df["premium"].max())
        if min_p < max_p:
            rng = st.slider("Premium Range (USD)", min_p, max_p, (min_p, max_p))
        else:
            rng = (min_p, max_p)
    with col_f3:
        sort_col = st.selectbox("Sort by", ["Date (Newest)", "Premium (High)", "Risk Score (High)"])

    # Apply filters
    filtered = df[df["product"].isin(prod_filter)]
    filtered = filtered[(filtered["premium"] >= rng[0]) & (filtered["premium"] <= rng[1])]

    if sort_col == "Premium (High)":
        filtered = filtered.sort_values("premium", ascending=False)
    elif sort_col == "Risk Score (High)":
        filtered = filtered.sort_values("risk_score", ascending=False)
    else:
        filtered = filtered.sort_values("created_at", ascending=False)

    st.markdown(f"**{len(filtered)} quote(s) found**")
    st.markdown("---")

    # ── Quote cards ───────────────────────────────────────────────────────────
    ICONS = {"Motor": "🚗", "Life": "❤️", "Property": "🏠", "Health": "🏥"}

    for _, row in filtered.iterrows():
        risk_label, risk_color = get_risk_category(row["risk_score"])
        icon = ICONS.get(row["product"], "📄")

        with st.expander(
            f"{icon} #{row['id']} — {row['insured']}  |  {row['product']}  |  "
            f"${row['premium']:,.2f}  |  Risk: {row['risk_score']:.0f}/100",
            expanded=False,
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("Annual Premium", f"${row['premium']:,.2f}")
            c2.metric("Monthly", f"${row['premium']/12:,.2f}")
            c3.metric("Risk Score", f"{row['risk_score']:.1f}")

            st.markdown(f"""
            <div style='margin:0.5rem 0; font-size:0.85rem;'>
                <b>Risk:</b> <span style='color:{risk_color};'>{risk_label}</span> &nbsp;|&nbsp;
                <b>Date:</b> {row['created_at'][:16]}
            </div>
            """, unsafe_allow_html=True)

            # Show inputs if stored
            # (inputs_json column not in query — reload if needed)
            del_col, _ = st.columns([1, 4])
            with del_col:
                if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                    delete_quote(row["id"], user["id"])
                    st.success("Quote deleted.")
                    st.rerun()

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Summary Table")
    disp = filtered[["id","product","insured","premium","risk_score","created_at"]].copy()
    disp.columns = ["ID","Product","Insured","Premium ($)","Risk Score","Created At"]
    disp["Premium ($)"] = disp["Premium ($)"].apply(lambda x: f"${x:,.2f}")
    disp["Created At"] = disp["Created At"].str[:16]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # ── CSV Download ──────────────────────────────────────────────────────────
    csv = filtered.to_csv(index=False)
    st.download_button(
        "⬇️  Download as CSV",
        data=csv,
        file_name="my_quotes.csv",
        mime="text/csv",
    )
