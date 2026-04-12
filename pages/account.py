import streamlit as st
from utils.auth import get_current_user, update_user_profile, change_password, get_conn


def show_account():
    st.markdown("## 👤 My Account")
    st.markdown("Manage your profile and security settings.")
    st.markdown("---")

    user = get_current_user()

    tab1, tab2, tab3 = st.tabs(["✏️  Edit Profile", "🔒  Change Password", "📋  Activity Log"])

    # ── Profile ───────────────────────────────────────────────────────────────
    with tab1:
        st.markdown(f"""
        <div class='iq-card' style='margin-bottom:1.5rem;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>👤</div>
            <div style='font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700;'>
                {user['full_name'] or user['username']}
            </div>
            <div style='color:#8899bb; font-size:0.85rem;'>@{user['username']} · {user['role'].title()}</div>
        </div>
        """, unsafe_allow_html=True)

        new_name  = st.text_input("Full Name",  value=user["full_name"] or "")
        new_email = st.text_input("Email",      value=user["email"] or "")

        if st.button("💾  Save Profile"):
            ok, msg = update_user_profile(user["id"], new_name, new_email)
            if ok:
                st.session_state.full_name = new_name
                st.session_state.email     = new_email
                st.success(msg)
            else:
                st.error(msg)

        st.markdown("---")
        st.markdown(f"""
        <div style='font-size:0.8rem; color:#8899bb;'>
            Account created via InsureIQ · Role: <b>{user['role']}</b>
        </div>
        """, unsafe_allow_html=True)

    # ── Password ──────────────────────────────────────────────────────────────
    with tab2:
        old_pw  = st.text_input("Current Password", type="password", key="cp_old")
        new_pw1 = st.text_input("New Password",     type="password", key="cp_new1")
        new_pw2 = st.text_input("Confirm New Password", type="password", key="cp_new2")

        if st.button("🔒  Update Password"):
            if new_pw1 != new_pw2:
                st.error("New passwords do not match.")
            else:
                ok, msg = change_password(user["id"], old_pw, new_pw1)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    # ── Activity Log ──────────────────────────────────────────────────────────
    with tab3:
        conn = get_conn()
        rows = conn.execute(
            "SELECT action, detail, ts FROM audit_log WHERE user_id=? ORDER BY ts DESC LIMIT 30",
            (user["id"],),
        ).fetchall()
        conn.close()

        if not rows:
            st.info("No activity recorded yet.")
        else:
            for action, detail, ts in rows:
                icon = "🔑" if action == "LOGIN" else "📝" if action == "REGISTER" else "⚡"
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:6px 0;
                     border-bottom:1px solid rgba(15,214,194,0.08); font-size:0.82rem;'>
                    <span>{icon} <b>{action}</b> — {detail}</span>
                    <span style='color:#8899bb;'>{ts[:16]}</span>
                </div>
                """, unsafe_allow_html=True)
