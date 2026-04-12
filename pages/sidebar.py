import streamlit as st


def show_sidebar() -> str:
    with st.sidebar:
        st.markdown(f"""
        <div style='padding: 1rem 0 0.5rem 0;'>
            <div class='logo-text'>🛡️ InsureIQ</div>
            <div class='logo-sub'>Actuarial Pricing Platform</div>
        </div>
        <hr>
        <div style='font-size:0.82rem; color:#8899bb; margin-bottom:0.3rem;'>Signed in as</div>
        <div style='font-weight:600; color:#0fd6c2; font-family:Syne,sans-serif;'>
            {st.session_state.get('full_name') or st.session_state.get('username','User')}
        </div>
        <div style='font-size:0.75rem; color:#8899bb; margin-bottom:1rem;'>
            @{st.session_state.get('username','')}
        </div>
        <hr>
        """, unsafe_allow_html=True)

        pages = {
            "📊  Dashboard":      "Dashboard",
            "💰  Price a Policy": "Price a Policy",
            "📁  My Quotes":      "My Quotes",
            "🔍  Risk Explorer":  "Risk Explorer",
            "🧠  Model Insights": "Model Insights",
            "👤  Account":        "Account",
        }

        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Dashboard"

        for label, key in pages.items():
            active = st.session_state.nav_page == key
            style = "background:rgba(15,214,194,0.12); border-radius:8px;" if active else ""
            if st.button(label, use_container_width=True, key=f"nav_{key}"):
                st.session_state.nav_page = key

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            for k in ["logged_in", "user_id", "username", "full_name", "email", "role", "nav_page"]:
                st.session_state.pop(k, None)
            st.rerun()

    return st.session_state.nav_page
