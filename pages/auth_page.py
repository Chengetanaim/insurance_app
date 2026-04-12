import streamlit as st
from utils.auth import login_user, register_user


def show_auth_page():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem 0;'>
            <div class='logo-text'>🛡️ InsureIQ</div>
            <div class='logo-sub'>Actuarial Pricing Platform</div>
            <p style='color:#8899bb; margin-top:0.5rem; font-size:0.9rem;'>
                GLM-powered insurance pricing for students & analysts
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑  Sign In", "📝  Create Account"])

        # ── LOGIN ────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="your_username", key="li_user")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True, key="btn_login"):
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, result = login_user(username, password)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = result["id"]
                        st.session_state.username   = result["username"]
                        st.session_state.full_name  = result["full_name"]
                        st.session_state.email      = result["email"]
                        st.session_state.role       = result["role"]
                        st.success(f"Welcome back, {result['full_name'] or result['username']}!")
                        st.rerun()
                    else:
                        st.error(result)

            st.markdown("""
            <div style='text-align:center; margin-top:1rem; color:#8899bb; font-size:0.8rem;'>
                Demo credentials — register a new account above
            </div>
            """, unsafe_allow_html=True)

        # ── REGISTER ─────────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            full_name  = st.text_input("Full Name",  placeholder="Tinashe Moyo",    key="rg_name")
            email      = st.text_input("Email",      placeholder="you@email.com",   key="rg_email")
            username_r = st.text_input("Username",   placeholder="tinashe_m",       key="rg_user")
            pw1        = st.text_input("Password",   type="password", placeholder="min. 6 characters", key="rg_pw1")
            pw2        = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="rg_pw2")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account", use_container_width=True, key="btn_register"):
                if not all([full_name, email, username_r, pw1, pw2]):
                    st.error("Please fill in all fields.")
                elif pw1 != pw2:
                    st.error("Passwords do not match.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                else:
                    ok, msg = register_user(username_r, email, pw1, full_name)
                    if ok:
                        st.success(msg + " Please sign in.")
                    else:
                        st.error(msg)
