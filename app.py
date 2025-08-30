import streamlit as st
from database import add_url, get_urls, delete_url, stop_monitoring, start_monitoring, get_history
from monitor import monitor_all
import asyncio
import pandas as pd
import plotly.express as px
import time

# --- Page Config ---
st.set_page_config(page_title="Website Monitoring Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Modernized CSS Styling ---
st.markdown("""
    <style>
        /* Main App Styling */
        .stApp {
            background-color: #0F1116;
            color: #FAFAFA;
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1A1C23;
        }
        [data-testid="stSidebar"] h2 {
            color: #00BFFF; /* Bright blue for sidebar headers */
        }
        
        /* Main Title */
        h1 {
            color: #00BFFF;
            text-align: center;
            font-weight: bold;
        }
        h2, h3 {
            color: #E0E0E0;
        }
        
        /* Status Card Styling */
        .status-card {
            background-color: #1A1C23;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2C2F38;
            text-align: center;
            transition: all 0.3s ease-in-out;
            height: 200px; /* Fixed height for uniform cards */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .status-card:hover {
            transform: translateY(-5px);
            border-color: #00BFFF;
            box-shadow: 0 4px 20px rgba(0, 191, 255, 0.15);
        }
        
        /* Status Indicator Dot */
        .status-dot {
            height: 20px;
            width: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-bottom: 10px;
            animation: pulse 2s infinite;
        }
        
        /* URL Text Styling - CORRECTED for truncation */
        .url-text {
            font-weight: bold;
            white-space: nowrap;     /* Don't wrap */
            overflow: hidden;        /* Hide overflow */
            text-overflow: ellipsis;  /* Add ... */
            font-size: 14px;
        }
        .status-text {
            font-size: 12px;
            color: #A0A0A0;
        }
        
        /* Button Styling inside Card */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #00BFFF;
            background-color: transparent;
            color: #00BFFF;
        }
        .stButton>button:hover {
            background-color: #00BFFF;
            color: #1A1C23;
            border-color: #00BFFF;
        }
        
        /* Keyframe for Pulse Animation */
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 191, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0); }
        }
    </style>
""", unsafe_allow_html=True)


# --- Main Dashboard Title ---
st.markdown("<h1>🌐 Website Monitoring Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")


# --- Session State Initialization ---
if "urls" not in st.session_state:
    st.session_state.urls = get_urls()

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🔧 Manage URLs")
    
    with st.form("add_url_form"):
        new_url = st.text_input("Add New URL", placeholder="https://example.com")
        submitted = st.form_submit_button("Add URL")
        if submitted and new_url.strip() != '':
            if add_url(new_url):
                st.toast(f"✅ URL '{new_url}' added!", icon="🎉")
                st.session_state.urls = get_urls()
                st.rerun()
            else:
                st.toast("⚠️ URL already exists!", icon="❗")

    urls_list = [u[1] for u in st.session_state.urls]
    if urls_list:
        st.header("⚙️ Global Controls")
        
        url_to_delete = st.selectbox("Select URL to Delete", options=urls_list)
        if st.button("Delete Selected URL", type="primary"):
            url_id = [u[0] for u in st.session_state.urls if u[1] == url_to_delete][0]
            stop_monitoring(url_id)
            delete_url(url_id)
            st.toast(f"🗑️ URL '{url_to_delete}' deleted!", icon="🗑️")
            st.session_state.urls = get_urls()
            st.rerun()

        if st.button("Start All Monitoring"):
            for row in st.session_state.urls:
                start_monitoring(row[0])
            st.session_state.urls = get_urls()
            st.toast("🚀 Started monitoring all URLs!", icon="🚀")
            st.rerun()
        
        if st.button("Stop All Monitoring"):
            for row in st.session_state.urls:
                stop_monitoring(row[0])
            st.session_state.urls = get_urls()
            st.toast("🛑 Stopped monitoring all URLs.", icon="🛑")
            st.rerun()


# --- Auto-refresh Monitoring ---
refresh_interval = 10  # seconds
if "last_run" not in st.session_state:
    st.session_state.last_run = 0

if time.time() - st.session_state.last_run > refresh_interval:
    with st.spinner("Checking website statuses..."):
        asyncio.run(monitor_all())
    st.session_state.last_run = time.time()
    st.session_state.urls = get_urls()
    # st.rerun() # <-- THIS LINE IS REMOVED TO FIX THE DOUBLE-CLICK ISSUE


# --- Live Status Grid ---
st.subheader("🖥️ Live Status")
urls_data = st.session_state.urls

if not urls_data:
    st.info("No URLs added yet. Add a URL from the sidebar to start monitoring.")
else:
    cols = st.columns(4)
    for i, (url_id, url, status, is_monitoring) in enumerate(urls_data):
        with cols[i % 4]:
            # Logic for better visual feedback
            if is_monitoring:
                status_color = "#28a745" if status == 'UP' else "#ff4b4b" if status == 'DOWN' else "#6c757d"
                display_status = status
            else:
                status_color = "#6c757d"  # Grey color for paused state
                display_status = "PAUSED" # Display "PAUSED" text

            history = get_history(url_id)
            last_resp_time = round(history[0][2], 2) if history else "N/A"
            tooltip = f"URL: {url}\nResponse Time: {last_resp_time} ms"
            
            st.markdown(f"""
                <div class="status-card" title="{tooltip}">
                    <div>
                        <span class="status-dot" style="background-color: {status_color};"></span>
                        <p class="url-text">{url}</p>
                        <p class="status-text">{display_status}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Button logic
            if is_monitoring:
                if st.button("Stop", key=f"stop_{url_id}"):
                    stop_monitoring(url_id)
                    st.session_state.urls = get_urls() # ✅ The fix
                    st.toast(f"Monitoring stopped for {url}", icon="🛑")
                    st.rerun()
            else:
                if st.button("Start", key=f"start_{url_id}"):
                    start_monitoring(url_id)
                    st.session_state.urls = get_urls() # ✅ The fix
                    st.toast(f"Monitoring started for {url}", icon="🚀")
                    st.rerun()

st.markdown("---")

# --- Analytics Dashboard with Tabs ---
st.subheader("📊 Analytics Dashboard")
agg_tab, ind_tab = st.tabs(["Aggregate Analytics", "Individual URL Analytics"])

with agg_tab:
    if not urls_data:
        st.warning("No data to display. Please add URLs.")
    else:
        agg_list = []
        for url_id, url, _, _ in urls_data:
            hist = get_history(url_id)
            if hist:
                hist_df = pd.DataFrame(hist, columns=['Timestamp', 'Status', 'Response Time'])
                total = len(hist_df)
                up = len(hist_df[hist_df['Status'] == 'UP'])
                down = total - up
                avg_resp = round(hist_df['Response Time'].mean(), 2)
                uptime_percent = round((up / total) * 100, 2) if total > 0 else 0
                agg_list.append([url, total, up, down, avg_resp, uptime_percent])
        
        if agg_list:
            agg_df = pd.DataFrame(agg_list, columns=['URL', 'Total Checks', 'UP', 'DOWN', 'Avg Response (ms)', 'Uptime %'])
            st.dataframe(agg_df, width='stretch')

            fig_all = px.bar(agg_df, x='URL', y='Uptime %', color='Uptime %',
                             color_continuous_scale=px.colors.sequential.Tealgrn, title="Uptime % of All URLs")
            fig_all.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_all, width='stretch')
        else:
            st.info("No monitoring history available yet.")

with ind_tab:
    if not urls_data:
        st.warning("No data to display. Please add URLs.")
    else:
        status_df = pd.DataFrame(urls_data, columns=['ID', 'URL', 'Status', 'Monitoring'])
        selected_url = st.selectbox("Select URL for Detailed Analysis", status_df['URL'])
        
        if selected_url:
            url_id = status_df[status_df['URL'] == selected_url]['ID'].values[0]
            history = get_history(url_id)

            if history:
                hist_df = pd.DataFrame(history, columns=['Timestamp', 'Status', 'Response Time'])
                hist_df['Timestamp'] = pd.to_datetime(hist_df['Timestamp'])
                
                total_checks = len(hist_df)
                up_checks = len(hist_df[hist_df['Status'] == 'UP'])
                uptime_percent = round((up_checks / total_checks) * 100, 2) if total_checks > 0 else 0
                avg_response = round(hist_df['Response Time'].mean(), 2)
                
                kpi1, kpi2 = st.columns(2)
                kpi1.metric(label="✅ Uptime Percentage", value=f"{uptime_percent}%")
                kpi2.metric(label="⚡ Average Response Time", value=f"{avg_response} ms")

                fig1 = px.line(hist_df, x='Timestamp', y='Response Time', title=f"{selected_url} Response Time History",
                               markers=True, template="plotly_dark")
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, width='stretch')

                csv = hist_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download History as CSV",
                    data=csv,
                    file_name=f"{selected_url}_history.csv",
                    mime='text/csv'
                )
            else:
                st.info("No history available for this URL yet.")




