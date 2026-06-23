# dashboard_v2.py
import streamlit as st
import json
import glob
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time

# Page config
st.set_page_config(
    page_title="TrendTracker Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== DARK MODE TOGGLE ====================
# Initialize theme in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Dark mode CSS
dark_css = """
<style>
    .stApp { background: #0f172a; color: #e2e8f0; }
    .main-header { color: #f8fafc !important; }
    .sub-header { color: #94a3b8 !important; }
    .trending-item { background: #1e293b !important; border-left-color: #60a5fa !important; }
    div[data-testid="stMetricValue"] { color: #f8fafc !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #1e293b !important; }
    .stTabs [data-baseweb="tab"] { color: #e2e8f0 !important; }
    .st-expander { background: #1e293b !important; border: 1px solid #334155 !important; }
</style>
"""

light_css = """
<style>
    .stApp { background: #ffffff; color: #1f2937; }
</style>
"""

# Apply theme
if st.session_state.dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    st.markdown(light_css, unsafe_allow_html=True)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .trending-item {
        background: #f9fafb;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        transition: all 0.3s ease;
    }
    .trending-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .sentiment-positive { color: #10b981; font-weight: 600; }
    .sentiment-negative { color: #ef4444; font-weight: 600; }
    .sentiment-mixed { color: #f59e0b; font-weight: 600; }
    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-youtube { background: #fecaca; color: #991b1b; }
    .badge-hackernews { background: #fed7aa; color: #9a3412; }
    .badge-devto { background: #bbf7d0; color: #166534; }
    .badge-github { background: #ddd6fe; color: #5b21b6; }
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 0.5rem;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .stButton>button {
        border-radius: 0.5rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
col_header, col_theme = st.columns([6, 1])

with col_header:
    st.markdown('<p class="main-header">📊 TrendTracker Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time social intelligence for business decisions</p>', unsafe_allow_html=True)

with col_theme:
    # Dark mode toggle in header
    if st.toggle("🌙", value=st.session_state.dark_mode, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Time range selector
    time_range = st.selectbox(
        "Analysis Period",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"],
        index=0
    )
    
    # Platform filters
    st.subheader("Platforms")
    platforms = {
        'YouTube': st.checkbox('YouTube', value=True),
        'Hacker News': st.checkbox('Hacker News', value=True),
        'Dev.to': st.checkbox('Dev.to', value=True),
        'GitHub': st.checkbox('GitHub', value=True)
    }
    
    # Keywords input
    st.subheader("Keywords")
    keywords_input = st.text_area(
        "Enter keywords (one per line)",
        "AI tools\nSaaS\nstartup funding\nremote work\nproductivity\nB2B marketing"
    )
    
    # Auto-refresh
    st.subheader("⏱️ Auto-Refresh")
    auto_refresh = st.toggle("Enable (5 min)", value=False)
    if auto_refresh:
        st.markdown('<span class="live-indicator"></span> Live', unsafe_allow_html=True)
        st.caption("Dashboard refreshes every 5 minutes")
    
    st.divider()
    
    # Export section in sidebar
    st.subheader("📥 Quick Export")
    
    st.divider()
    st.caption("v2.1.0 | TrendTracker Pro")

# ==================== LOAD DATA WITH SPINNER ====================
with st.spinner("🔄 Analyzing trends and loading data..."):
    @st.cache_data(ttl=60)
    def load_data():
        files = glob.glob("reports/*.json") + glob.glob("report_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getmtime)
        with open(latest, encoding='utf-8') as f:
            return json.load(f)
    
    data = load_data()
    
    # Simulate processing delay for UX
    time.sleep(0.5)

if not data:
    st.error("⚠️ No reports found")
    st.info("Run `python main.py` to generate your first report")
    
    # Demo mode with sample data
    if st.button("🎮 Load Demo Data"):
        demo_data = {
            "generated_at": datetime.now().isoformat(),
            "keywords_searched": ["AI", "SaaS", "startup"],
            "total_posts_analyzed": 150,
            "trending_topics": [
                {
                    "topic": "artificial intelligence",
                    "mention_count": 45,
                    "engagement_score": 1250.5,
                    "sentiment": {"positive": 30, "negative": 10, "positive_pct": 75.0},
                    "platforms": ["youtube", "hackernews"],
                    "trending_velocity": "📈 rising",
                    "sample_posts": [
                        {"text": "New AI tools for business automation...", "url": "#", "platform": "youtube"}
                    ]
                }
            ],
            "summary": {
                "sentiment_overview": {"overall": "positive", "positive_pct": 75.0}
            }
        }
        st.session_state.demo_data = demo_data
        st.rerun()
    st.stop()

# Use demo data if loaded
if 'demo_data' in st.session_state and st.session_state.demo_data:
    data = st.session_state.demo_data
    st.success("✅ Demo mode active")

# ==================== EXPORT FUNCTIONALITY ====================
# Prepare export data
export_json = json.dumps(data, indent=2, default=str)
export_csv = None

# Create CSV from trending topics
if data.get('trending_topics'):
    csv_data = []
    for t in data['trending_topics']:
        csv_data.append({
            'Topic': t.get('topic', ''),
            'Mentions': t.get('mention_count', 0),
            'Engagement': t.get('engagement_score', 0),
            'Sentiment': t.get('sentiment', {}).get('positive_pct', 0),
            'Platforms': ', '.join(t.get('platforms', [])),
            'Velocity': t.get('trending_velocity', '')
        })
    export_csv = pd.DataFrame(csv_data).to_csv(index=False)

# Download buttons in sidebar
with st.sidebar:
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "📄 JSON",
            export_json,
            file_name=f"trendtracker_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_dl2:
        if export_csv is not None:
            st.download_button(
                "📊 CSV",
                export_csv,
                file_name=f"trendtracker_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📊 CSV", disabled=True, use_container_width=True)

# ==================== AUTO-REFRESH ====================
if auto_refresh:
    # Countdown timer
    refresh_placeholder = st.empty()
    refresh_placeholder.info("⏳ Auto-refresh in 5:00")
    
    # JavaScript auto-refresh (more reliable than Python loop)
    st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 300000);  // 5 minutes
    </script>
    """, unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================
def safe_get(d, *keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d

def get_platform_badge(platform):
    platform = platform.lower()
    if 'youtube' in platform:
        return '<span class="platform-badge badge-youtube">YouTube</span>'
    elif 'hackernews' in platform or 'hacker' in platform:
        return '<span class="platform-badge badge-hackernews">Hacker News</span>'
    elif 'devto' in platform or 'dev' in platform:
        return '<span class="platform-badge badge-devto">Dev.to</span>'
    elif 'github' in platform:
        return '<span class="platform-badge badge-github">GitHub</span>'
    return f'<span class="platform-badge">{platform}</span>'

# ==================== METRICS ROW ====================
st.subheader("📈 Key Metrics")

total_posts = data.get('total_posts_analyzed', 0)
trending_topics = data.get('trending_topics', [])
sentiment_overview = safe_get(data, 'summary', 'sentiment_overview', default={})
generated_at = data.get('generated_at', '')

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    delta = "↑ Live" if total_posts > 200 else None
    st.metric("Total Posts", f"{total_posts:,}", delta=delta)

with m2:
    rising_count = len([t for t in trending_topics if 'rising' in t.get('trending_velocity', '')])
    st.metric("Trending Topics", len(trending_topics), delta=f"+{rising_count} rising")

with m3:
    sentiment = sentiment_overview.get('overall', 'neutral').upper()
    emoji = "🟢" if sentiment == 'POSITIVE' else "🔴" if sentiment == 'NEGATIVE' else "🟡"
    st.metric("Overall Sentiment", f"{emoji} {sentiment}")

with m4:
    pos_pct = sentiment_overview.get('positive_pct', 50)
    st.metric("Positive Ratio", f"{pos_pct}%")

with m5:
    try:
        gen_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
        time_ago = datetime.now(gen_time.tzinfo) - gen_time
        hours_ago = int(time_ago.total_seconds() / 3600)
        st.metric("Last Updated", f"{hours_ago}h ago" if hours_ago > 0 else "Just now")
    except:
        st.metric("Last Updated", "Unknown")

st.divider()

# ==================== MAIN CONTENT ====================
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🔥 Trending Topics")
    
    if trending_topics:
        for i, topic in enumerate(trending_topics[:15], 1):
            topic_name = topic.get('topic', 'Unknown').upper()
            mentions = topic.get('mention_count', 0)
            engagement = round(topic.get('engagement_score', 0), 1)
            velocity = topic.get('trending_velocity', '')
            sentiment = topic.get('sentiment', {})
            pos_pct = sentiment.get('positive_pct', 0)
            platforms = topic.get('platforms', [])
            sample_posts = topic.get('sample_posts', [])
            
            velocity_icon = "🚀" if "rising_fast" in velocity else "📈" if "rising" in velocity else "📉" if "falling" in velocity else "➡️"
            
            with st.container():
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    st.markdown(f"""
                    <div class="trending-item">
                        <h4>{i}. {topic_name} {velocity_icon}</h4>
                        <p style="margin: 0.5rem 0;">
                            {' '.join([get_platform_badge(p) for p in platforms])}
                        </p>
                        <p style="color: #6b7280; font-size: 0.9rem;">
                            {mentions} mentions · {engagement} engagement score
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=pos_pct,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Pos%"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#10b981" if pos_pct > 60 else "#f59e0b" if pos_pct > 40 else "#ef4444"},
                            'steps': [
                                {'range': [0, 40], 'color': "#fef2f2"},
                                {'range': [40, 60], 'color': "#fffbeb"},
                                {'range': [60, 100], 'color': "#ecfdf5"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 2},
                                'thickness': 0.75,
                                'value': 50
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{i}")
                
                with st.expander(f"🔍 View details for {topic_name}"):
                    st.write("**Sample Posts:**")
                    for post in sample_posts[:3]:
                        platform = post.get('platform', 'link').upper()
                        text = post.get('text', 'No text')[:200]
                        url = post.get('url', '#')
                        st.markdown(f"- **[{platform}]** {text}... [Read more]({url})")
                    
                    st.write("**Sentiment Breakdown:**")
                    st.progress(pos_pct / 100, text=f"{pos_pct}% Positive")
                    
                    # Share button
                    if st.button(f"🔗 Share {topic_name}", key=f"share_{i}"):
                        st.code(f"Trending: {topic_name} - {mentions} mentions, {pos_pct}% positive", language=None)
    else:
        st.info("No trending topics found. Try different keywords.")

with right_col:
    st.subheader("📡 Live Feed")
    
    activities = [
        {"time": "2m ago", "platform": "YouTube", "action": "New video: 'AI Tools for Business'"},
        {"time": "5m ago", "platform": "Hacker News", "action": "Post reached 500 upvotes"},
        {"time": "12m ago", "platform": "Dev.to", "action": "Article: 'SaaS Pricing Strategies'"},
        {"time": "18m ago", "platform": "GitHub", "action": "Repo starred 200+ times"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style="padding: 0.75rem; background: {'#1e293b' if st.session_state.dark_mode else '#f3f4f6'}; border-radius: 0.5rem; margin: 0.5rem 0;">
            <small style="color: #9ca3af;">{activity['time']}</small><br>
            <strong>{activity['platform']}</strong>: {activity['action']}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("⚡ Quick Stats")
    
    platform_counts = {}
    for t in trending_topics:
        for p in t.get('platforms', []):
            platform_counts[p] = platform_counts.get(p, 0) + 1
    
    if platform_counts:
        fig_pie = px.pie(
            values=list(platform_counts.values()),
            names=list(platform_counts.keys()),
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(showlegend=True, height=250)
        st.plotly_chart(fig_pie, use_container_width=True, key="platform_pie")

# ==================== ANALYTICS TABS ====================
st.divider()
st.subheader("📊 Detailed Analytics")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Sentiment Trends", "📡 Platform Comparison", "☁️ Keyword Cloud", "📋 Raw Data"])

with tab1:
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    sentiment_df = pd.DataFrame({
        'Date': dates,
        'Positive': [65, 68, 72, 70, 75, 78, 80],
        'Negative': [35, 32, 28, 30, 25, 22, 20]
    })
    
    fig_sentiment = px.line(
        sentiment_df,
        x='Date',
        y=['Positive', 'Negative'],
        title="Sentiment Trend (Last 7 Days)",
        template="plotly_dark" if st.session_state.dark_mode else "plotly_white"
    )
    st.plotly_chart(fig_sentiment, use_container_width=True, key="sentiment_trend")

with tab2:
    if platform_counts:
        platform_df = pd.DataFrame([
            {'Platform': k, 'Mentions': v}
            for k, v in platform_counts.items()
        ])
        fig_bar = px.bar(
            platform_df,
            x='Platform',
            y='Mentions',
            color='Platform',
            title="Mentions by Platform",
            template="plotly_dark" if st.session_state.dark_mode else "plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="platform_bar")

with tab3:
    all_keywords = []
    for t in trending_topics:
        all_keywords.extend([t.get('topic', '')] * t.get('mention_count', 1))
    
    if all_keywords:
        keyword_freq = pd.Series(all_keywords).value_counts().head(20)
        fig_cloud = px.bar(
            x=keyword_freq.values,
            y=keyword_freq.index,
            orientation='h',
            title="Top Keywords",
            template="plotly_dark" if st.session_state.dark_mode else "plotly_white"
        )
        st.plotly_chart(fig_cloud, use_container_width=True, key="keyword_cloud")

with tab4:
    st.write("**Full Report Data:**")
    st.json(data)
    
    st.download_button(
        "📥 Download Full JSON",
        export_json,
        file_name=f"trendtracker_full_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

# ==================== FOOTER ====================
st.divider()
st.caption("© 2026 TrendTracker Pro | Built with ❤️ for data-driven decisions")