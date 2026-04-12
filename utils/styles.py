import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --navy:    #0b1629;
        --navy2:   #112240;
        --teal:    #0fd6c2;
        --teal2:   #0aab9a;
        --amber:   #f5a623;
        --red:     #ef4444;
        --green:   #22c55e;
        --text:    #e2eaf6;
        --muted:   #8899bb;
        --card:    rgba(17,34,64,0.85);
        --border:  rgba(15,214,194,0.15);
    }

    html, body, [class*="css"]  {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--navy) !important;
        color: var(--text) !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Syne', sans-serif !important;
        color: var(--text) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--navy2) !important;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * { color: var(--text) !important; }

    /* Inputs */
    .stTextInput input, .stSelectbox > div > div, .stNumberInput input,
    .stPasswordInput input {
        background: var(--navy2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }
    .stSelectbox > div > div > div { color: var(--text) !important; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--teal), var(--teal2)) !important;
        color: var(--navy) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(15,214,194,0.3) !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricValue"] { color: var(--teal) !important; font-family: 'Syne', sans-serif !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: var(--navy2) !important; border-radius: 10px !important; }
    .stTabs [data-baseweb="tab"] { color: var(--muted) !important; }
    .stTabs [aria-selected="true"] { color: var(--teal) !important; }

    /* DataFrames */
    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 10px !important; }

    /* Divider */
    hr { border-color: var(--border) !important; }

    /* Alerts */
    .stAlert { border-radius: 10px !important; }

    /* Success / info overrides */
    .element-container .stAlert [data-baseweb="notification"] {
        background: rgba(34,197,94,0.1) !important;
        border-left: 3px solid var(--green) !important;
    }

    /* Custom card class */
    .iq-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .iq-card h3 { margin-top: 0; color: var(--teal) !important; }
    .iq-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Syne', sans-serif;
    }
    .badge-low    { background: rgba(34,197,94,0.15);  color: #22c55e; }
    .badge-med    { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-high   { background: rgba(249,115,22,0.15); color: #f97316; }
    .badge-vhigh  { background: rgba(239,68,68,0.15);  color: #ef4444; }

    /* Logo text */
    .logo-text {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--teal);
        letter-spacing: -1px;
    }
    .logo-sub {
        font-size: 0.7rem;
        color: var(--muted);
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Hide default hamburger / footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
