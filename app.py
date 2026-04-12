import streamlit as st
from utils.auth import init_db, get_current_user
from utils.styles import apply_styles

st.set_page_config(
    page_title="InsureIQ — Actuarial Pricing Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
init_db()

# ── Session bootstrap ────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ── Routing ──────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    from pages.auth_page import show_auth_page
    show_auth_page()
else:
    from pages.sidebar import show_sidebar
    page = show_sidebar()

    if page == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "Price a Policy":
        from pages.pricer import show_pricer
        show_pricer()
    elif page == "My Quotes":
        from pages.quotes import show_quotes
        show_quotes()
    elif page == "Risk Explorer":
        from pages.risk_explorer import show_risk_explorer
        show_risk_explorer()
    elif page == "Model Insights":
        from pages.model_insights import show_model_insights
        show_model_insights()
    elif page == "Account":
        from pages.account import show_account
        show_account()
