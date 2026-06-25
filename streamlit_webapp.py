import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orches",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 0 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

.sidebar-title {
    font-size: 20px;
    font-weight: 600;
    color: #e6edf3 !important;
    letter-spacing: -0.3px;
    padding: 24px 16px 8px;
    border-bottom: 1px solid #1e2130;
    margin-bottom: 16px;
}

.sidebar-subtitle {
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6e7681 !important;
    padding: 0 16px;
    margin-bottom: 8px;
}

/* ── History item ── */
.history-item {
    background: #161b22;
    border: 1px solid #1e2130;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 12px;
    cursor: pointer;
    transition: border-color 0.15s;
}
.history-item:hover { border-color: #388bfd; }
.history-item .query-text {
    font-size: 13px;
    color: #c9d1d9 !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.history-item .route-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 2px 7px;
    border-radius: 4px;
    margin-bottom: 4px;
}

/* Route badge colors */
.badge-db       { background: #1f3d1f; color: #56d364 !important; }
.badge-maths    { background: #1e2d4a; color: #79c0ff !important; }
.badge-search   { background: #2d1f3d; color: #d2a8ff !important; }
.badge-weather  { background: #3d2d1f; color: #ffa657 !important; }

/* ── Main chat area ── */
.main-wrapper {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #0d1117;
    padding: 0;
}

.chat-header {
    padding: 20px 32px 16px;
    border-bottom: 1px solid #1e2130;
    background: #0d1117;
}

.chat-header h1 {
    font-size: 18px;
    font-weight: 600;
    color: #e6edf3;
    margin: 0;
    letter-spacing: -0.2px;
}

.chat-header p {
    font-size: 13px;
    color: #6e7681;
    margin: 2px 0 0;
}

/* ── Messages ── */
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
}

.msg-row { margin-bottom: 24px; }

.msg-user {
    display: flex;
    justify-content: flex-end;
}

.msg-user .bubble {
    background: #1f6feb;
    color: #ffffff;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.5;
}

.msg-assistant { display: flex; align-items: flex-start; gap: 12px; }

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, #388bfd, #6e40c9);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.msg-assistant .bubble {
    background: #161b22;
    border: 1px solid #1e2130;
    border-radius: 4px 16px 16px 16px;
    padding: 14px 16px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.6;
    color: #c9d1d9;
}

.msg-assistant .bubble p { margin: 0 0 8px; }
.msg-assistant .bubble p:last-child { margin-bottom: 0; }

/* ── Meta tags below assistant bubble ── */
.msg-meta {
    display: flex;
    gap: 8px;
    margin-top: 6px;
    margin-left: 44px;
    flex-wrap: wrap;
}

.meta-tag {
    font-size: 11px;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
}

.meta-route-db      { background: #1f3d1f; color: #56d364; }
.meta-route-maths   { background: #1e2d4a; color: #79c0ff; }
.meta-route-search  { background: #2d1f3d; color: #d2a8ff; }
.meta-route-weather { background: #3d2d1f; color: #ffa657; }

.meta-sql {
    background: #1c1c2e;
    color: #8b949e;
    border: 1px solid #2d2d4e;
    cursor: pointer;
}

/* ── SQL expander ── */
.sql-block {
    background: #0d1117;
    border: 1px solid #2d2d4e;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0 0 44px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #8b949e;
    white-space: pre-wrap;
}

/* ── Input area ── */
.input-area {
    padding: 16px 32px 24px;
    border-top: 1px solid #1e2130;
    background: #0d1117;
}

/* Streamlit input overrides */
.stTextInput > div > div > input {
    background: #161b22 !important;
    border: 1px solid #1e2130 !important;
    border-radius: 12px !important;
    color: #e6edf3 !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56, 139, 253, 0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #6e7681 !important; }

/* Streamlit button */
.stButton > button {
    background: #238636 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 14px 24px !important;
    font-family: 'Inter', sans-serif !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #2ea043 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 4px; }

/* Spinner */
.stSpinner > div { border-top-color: #388bfd !important; }
</style>
""", unsafe_allow_html=True)


# ── Lazy import graph (so streamlit doesn't crash on reload) ───────────────────
@st.cache_resource(show_spinner=False)
def load_graph():
    from master_node import app
    return app


# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   
    # each item: {"query": str, "answer": str, "route": str, "sql_query": str|None}


# ── Route badge helper ─────────────────────────────────────────────────────────
ROUTE_ICONS = {
    "db":          "🗄️",
    "maths":       "🧮",
    "search":      "🔍",
    "get_weather": "🌤️",
}

ROUTE_LABELS = {
    "db":          "Database",
    "maths":       "Maths",
    "search":      "Web Search",
    "get_weather": "Weather",
}

def route_badge_html(route: str, style: str = "sidebar") -> str:
    icon  = ROUTE_ICONS.get(route, "🤖")
    label = ROUTE_LABELS.get(route, route)
    key   = route.replace("_", "").replace("get", "")
    if route == "get_weather": key = "weather"
    if style == "sidebar":
        return f'<span class="route-badge badge-{key}">{icon} {label}</span>'
    return f'<span class="meta-tag meta-route-{key}">{icon} {label}</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 Orches</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Session History</div>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            '<p style="color:#6e7681;font-size:13px;padding:0 16px;">No queries yet.</p>',
            unsafe_allow_html=True
        )
    else:
        for i, item in enumerate(reversed(st.session_state.chat_history)):
            badge = route_badge_html(item["route"], style="sidebar")
            query_short = item["query"][:45] + "…" if len(item["query"]) > 45 else item["query"]
            st.markdown(f"""
            <div class="history-item">
                {badge}
                <div class="query-text">{query_short}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ── Main layout ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h1>Multi-Agent Assistant</h1>
    <p>Ask about your database, maths, current events, or weather.</p>
</div>
""", unsafe_allow_html=True)


# ── Render chat messages ───────────────────────────────────────────────────────
for item in st.session_state.chat_history:
    # User bubble
    st.markdown(f"""
    <div class="msg-row msg-user">
        <div class="bubble">{item["query"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # Assistant bubble
    route_tag = route_badge_html(item["route"], style="meta")
    st.markdown(f"""
    <div class="msg-row msg-assistant">
        <div class="avatar">✦</div>
        <div class="bubble">{item["answer"]}</div>
    </div>
    <div class="msg-meta">
        {route_tag}
    </div>
    """, unsafe_allow_html=True)

    # SQL block (only for db route)
    if item["route"] == "db" and item.get("sql_query"):
        with st.expander("📋 View SQL query", expanded=False):
            st.code(item["sql_query"], language="sql")


# ── Input area ────────────────────────────────────────────────────────────────
# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

user_input = st.chat_input(
    "Ask anything — database, maths, search, weather…"
)


# ── Run agent ─────────────────────────────────────────────────────────────────
if user_input:
    query = user_input

    with st.spinner("Thinking…"):
        try:
            graph = load_graph()
            result = graph.invoke({"user_request": query})

            # extract answer
            messages = result.get("messages", [])
            answer = messages[-1].content if messages else "No response."

            # extract route
            route = result.get("route", "db")

            # extract sql_query (only present for db route)
            sql_query = result.get("sql_query", None) if route == "db" else None

            # save to history
            st.session_state.chat_history.append({
                "query":     query,
                "answer":    answer,
                "route":     route,
                "sql_query": sql_query,
            })

        except Exception as e:
            st.session_state.chat_history.append({
                "query":     query,
                "answer":    f"⚠️ Error: {str(e)}",
                "route":     "db",
                "sql_query": None,
            })

    st.rerun()