import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.pricing import ALL_FACTORS, BASE_RATES


def show_model_insights():
    st.markdown("## 🧠 Model Insights")
    st.markdown("Understand the actuarial GLM methodology powering InsureIQ.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📚  Methodology", "📈  Factor Profiles", "🔢  Rate Tables"])

    # ── Tab 1: Methodology ────────────────────────────────────────────────────
    with tab1:
        col_text, col_formula = st.columns([3, 2])
        with col_text:
            st.markdown("""
            ### Generalised Linear Model (GLM) Pricing
            InsureIQ uses a **multiplicative log-linear GLM** — the industry-standard
            approach used by insurance companies globally for personal lines pricing.

            #### How It Works
            1. **Base Rate** — Starting premium for a standard/average risk profile.
            2. **Rating Factors** — Each underwriting variable (age, cover type, etc.)
               contributes a multiplier derived from historical loss data.
            3. **Composite Factor** — All individual factors are multiplied together.
            4. **Final Premium** — Base Rate × Composite Factor (+ any loadings).

            #### The Formula
            ```
            Premium = Base Rate × F₁ × F₂ × ... × Fₙ
            ```
            Where each Fᵢ represents a factor value ≥ 0. Values > 1 load the premium,
            values < 1 discount it.

            #### Risk Score
            The risk score (0–100) is a normalised composite of all factor values:
            - **< 30**: Low Risk (green)
            - **30–55**: Moderate Risk (amber)
            - **55–75**: High Risk (orange)
            - **75+**: Very High Risk (red)

            #### Why GLM?
            - **Interpretable**: Each factor's effect is explicit and auditable.
            - **Actuarially sound**: Factors can be derived from credibility-weighted experience studies.
            - **Multiplicative**: Interactions between factors are modelled naturally.
            - **Regulatory accepted**: Standard for IFRS 17, ZICARP and Solvency II reserving.
            """)

        with col_formula:
            # Visualise a sample build-up
            factors_demo = [1.0, 1.25, 1.0, 0.75, 1.6, 0.82]
            labels_demo  = ["Base", "×Age", "×Use", "×NCD", "×Cover", "Discount"]
            running = [1200]
            for f in factors_demo[1:]:
                running.append(running[-1] * f)

            fig = go.Figure(go.Funnel(
                y=labels_demo,
                x=running,
                textinfo="value+percent initial",
                marker={"color": ["#0fd6c2","#f5a623","#0fd6c2","#22c55e","#ef4444","#22c55e"]},
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2eaf6", title="Sample Premium Build-up",
                margin=dict(t=40, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        ---
        ### References
        - McCullagh & Nelder (1989) — *Generalized Linear Models*
        - Ohlsson & Johansson (2010) — *Non-Life Insurance Pricing with GLM*
        - ASSA (Actuarial Society of South Africa) — Technical papers on IFRS 17
        - Claxon Actuaries — *Insurance Product Pricing frameworks, Zimbabwe*
        """)

    # ── Tab 2: Factor Profiles ────────────────────────────────────────────────
    with tab2:
        st.markdown("**Visual comparison of rating factor multipliers across all products.**")
        prod = st.selectbox("Product", list(BASE_RATES.keys()), key="fi_prod")
        facs = ALL_FACTORS[prod]

        for fk, opts in facs.items():
            label = fk.replace("_", " ").title()
            keys  = list(opts.keys())
            vals  = list(opts.values())
            colors = ["#22c55e" if v < 1.0 else "#f5a623" if v <= 1.3 else "#ef4444" for v in vals]

            fig = go.Figure(go.Bar(
                x=keys, y=vals,
                marker_color=colors,
                text=[f"×{v:.2f}" for v in vals],
                textposition="outside",
            ))
            fig.add_hline(y=1.0, line_dash="dash", line_color="#8899bb",
                          annotation_text="Neutral (×1.00)", annotation_position="right")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2eaf6", title=f"{label} Factors",
                yaxis_title="Multiplier", height=280,
                margin=dict(t=40, b=40, l=10, r=10),
                xaxis_tickangle=-15,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 3: Rate Tables ────────────────────────────────────────────────────
    with tab3:
        st.markdown("**Full rating factor tables used in the pricing engine.**")
        prod_t = st.selectbox("Product", list(BASE_RATES.keys()), key="rt_prod")
        facs_t = ALL_FACTORS[prod_t]

        st.markdown(f"**Base Rate: ${BASE_RATES[prod_t]:,.0f} p.a.**")
        for fk, opts in facs_t.items():
            label = fk.replace("_", " ").title()
            df = pd.DataFrame(
                [(k, v, f"×{v:.2f}", f"{(v-1)*100:+.0f}%") for k, v in opts.items()],
                columns=["Option", "Factor Value", "Multiplier", "Impact vs Neutral"],
            )
            st.markdown(f"##### {label}")
            st.dataframe(df, use_container_width=True, hide_index=True)
