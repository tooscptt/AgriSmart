import streamlit as st
import google.generativeai as genai
import PIL.Image
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgriSmart OS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS HACK: METALLIC PURPLE & GLASSMORPHISM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp { background-color: #0a0510 !important; color: #f4f4f9 !important; overflow-x: hidden; }
    
    .glow-orb { position: fixed; border-radius: 50%; filter: blur(120px); opacity: 0.25; z-index: 0; pointer-events: none; }
    .orb-1 { width: 50vw; height: 50vw; background: #b06ab3; top: -20%; left: -10%; }
    .orb-2 { width: 40vw; height: 40vw; background: #452c63; bottom: -10%; right: -10%; }

    .block-container { z-index: 10 !important; position: relative !important; }

    h1, h2, h3 {
        background: linear-gradient(135deg, #b06ab3 0%, #452c63 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important; letter-spacing: -0.5px;
    }

    div[data-testid="metric-container"], div[data-testid="stForm"], div[data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(176, 106, 179, 0.2) !important;
        border-radius: 20px !important; padding: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(176, 106, 179, 0.05) !important;
        transition: 0.4s ease !important;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) !important; border-color: #b06ab3 !important;
        box-shadow: 0 15px 35px rgba(176, 106, 179, 0.2), inset 0 0 20px rgba(176, 106, 179, 0.1) !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 5, 16, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(176, 106, 179, 0.15) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #b06ab3 0%, #452c63 100%) !important;
        color: white !important; border: none !important; border-radius: 30px !important;
        padding: 10px 30px !important; font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(176, 106, 179, 0.4) !important; transition: 0.3s !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(176, 106, 179, 0.6) !important; }

    [data-testid="stMetricValue"] { color: #e0b0ff !important; font-weight: 800 !important; }
    .stRadio label { font-weight: 600 !important; color: #a99bb8 !important; padding: 5px 0; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
""", unsafe_allow_html=True)

# --- 3. SECURITY & AI INITIALIZATION ---
try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        st.error("🔒 API Key not found in Secrets!")
        st.stop()
except:
    st.error("Configuration error occurred.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Setup Mock Database
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': 'admin123'}

# --- 4. POPUP MODAL DIALOG (LOGIN/REGISTER) ---
@st.dialog("🔐 System Authentication")
def login_popup():
    st.write("Please sign in or create an account to unlock all features.")
    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])
    
    # LOGIN TAB
    with tab_login:
        username = st.text_input("Username", key="log_user")
        password = st.text_input("Password", type="password", key="log_pass")
        if st.button("Sign In ➔", use_container_width=True):
            with st.spinner("Connecting..."):
                time.sleep(1) 
                if username in st.session_state['users_db'] and st.session_state['users_db'][username] == password:
                    st.session_state['is_logged_in'] = True
                    st.session_state['current_user'] = username
                    st.rerun() # Refresh to close popup and unlock features
                else:
                    st.error("❌ Invalid username or password!")
        st.caption("💡 **Demo:** User: `admin` | Pass: `admin123`")

    # REGISTER TAB
    with tab_register:
        new_username = st.text_input("Choose Username", key="reg_user")
        new_password = st.text_input("Create Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_conf")
        if st.button("Register Account ➔", use_container_width=True):
            with st.spinner("Creating account..."):
                time.sleep(1)
                if new_username in st.session_state['users_db']:
                    st.error("❌ Username already exists!")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif len(new_username) < 3:
                    st.error("❌ Username too short!")
                else:
                    st.session_state['users_db'][new_username] = new_password
                    st.success("✅ Registration successful! Please Sign In.")

# --- 5. TWENTY (20) EXCLUSIVE FEATURES ---
def f1_dashboard():
    st.title("Main Dashboard (Preview)")
    if not st.session_state.get('is_logged_in', False):
        st.info("👀 **Guest Mode:** You are viewing the live dashboard. Please login to interact with other features.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Air Temperature", "26.8°C", "Normal")
    c2.metric("Humidity", "65%", "+2%")
    c3.metric("Soil pH", "6.7", "Ideal")
    c4.metric("AI Health", "98%", "Optimal")
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("**Daily Microclimate Trends**")
    st.line_chart(pd.DataFrame(np.random.randn(20, 2), columns=['Soil Temp', 'Humidity']))

def f2_iot_monitor():
    st.title("IoT Sensor Monitor")
    st.write("Real-time monitoring of agricultural microcontrollers.")
    st.progress(65, "Irrigation Water Capacity (65%)")
    st.progress(85, "IoT Battery Status (85%)")

def f3_irrigation():
    st.title("Automated Irrigation Control")
    c1, c2 = st.columns(2)
    with c1:
        st.toggle("Drip Pump - Block A", value=True)
        st.toggle("Sprinkler - Block B")
    with c2: st.info("Watering system is currently active in Block A.")

def f4_ai_doctor():
    st.title("AI Plant Doctor")
    img_file = st.file_uploader("Upload leaf/plant photo...", type=["jpg", "png"])
    if img_file:
        st.image(img_file, width=300)
        if st.button("Scan with AI ➔"):
            with st.spinner("Analyzing pixels..."):
                prompt = "Analyze this plant image. Provide the disease diagnosis, organic solutions, and chemical solutions in English."
                res = model.generate_content([prompt, PIL.Image.open(img_file)])
                st.success("Analysis Complete!")
                st.write(res.text)

def f5_chatbot():
    st.title("AI Consultant Chatbot")
    if "ai_chat" not in st.session_state: st.session_state.ai_chat = []
    for c in st.session_state.ai_chat:
        with st.chat_message(c["role"]): st.write(c["content"])
    usr_msg = st.chat_input("Ask any agricultural question...")
    if usr_msg:
        st.session_state.ai_chat.append({"role": "user", "content": usr_msg})
        st.chat_message("user").write(usr_msg)
        with st.spinner("Thinking..."):
            reply = model.generate_content("You are an expert agriculture consultant. Answer in English: " + usr_msg).text
            st.chat_message("assistant").write(reply)
            st.session_state.ai_chat.append({"role": "assistant", "content": reply})

def f6_calculator():
    st.title("Seed & Fertilizer Calculator")
    c1, c2 = st.columns(2)
    area = c1.number_input("Land Area (Hectares)", value=1.0)
    crop = c2.selectbox("Crop Type", ["Rice", "Corn", "Chili"])
    if st.button("Calculate Estimation"):
        st.metric("Estimated Seed Required", f"{area * (25 if crop=='Rice' else 15)} Kg")
        st.metric("Estimated NPK Fertilizer", f"{area * 300} Kg")

def f7_market_prices():
    st.title("Market Price Tracker")
    df = pd.DataFrame({"Commodity": ["Premium Rice", "Corn", "Chili", "Onion"], "Price/Kg (IDR)": [16500, 5200, 65000, 32000]})
    st.dataframe(df, use_container_width=True)

def f8_financials():
    st.title("Financial Projection (ROI)")
    capital = st.number_input("Total Capital (IDR)", value=5000000)
    revenue = st.number_input("Estimated Revenue (IDR)", value=8500000)
    profit = revenue - capital
    st.metric("Net Profit", f"IDR {profit:,.0f}")

def f9_weather():
    st.title("Weather & Climate Radar")
    c1, c2, c3 = st.columns(3)
    c1.metric("Today", "Moderate Rain")
    c2.metric("Tomorrow", "Cloudy")
    c3.metric("Day After", "Sunny")

def f10_calendar():
    st.title("Smart Planting Calendar")
    date_start = st.date_input("Start Planting Date", datetime.now())
    st.write(f"Estimated Harvest Season: **{date_start + timedelta(days=100)}**")

def f11_machinery():
    st.title("Machinery Management")
    st.checkbox("Tractor A (Ready)", value=True)
    st.checkbox("Sprayer Drone (Needs Charging)")

def f12_inventory():
    st.title("Warehouse Inventory")
    st.data_editor(pd.DataFrame({"Item": ["Urea", "NPK", "Pesticide"], "Stock": [50, 45, 10]}), use_container_width=True)

def f13_workers():
    st.title("Worker Management")
    st.success("Team A: Fertilizing North Block (Completed)")

def f14_soil():
    st.title("Soil Quality Test")
    c1, c2 = st.columns(2)
    c1.metric("Nitrogen", "High")
    c2.metric("Phosphorus", "Medium")

def f15_satellite():
    st.title("Satellite Mapping")
    st.map(pd.DataFrame(np.random.randn(10, 2) / [100, 100] + [-6.75, 108.5], columns=['lat', 'lon']))

def f16_cctv():
    st.title("Live CCTV")
    st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800", caption="CCTV Block A")

def f17_encyclopedia():
    st.title("Pest Encyclopedia")
    st.info("Database for handling leafhoppers, rats, and other agricultural pests.")

def f18_news():
    st.title("AgroTech News")
    st.write("New drought-resistant crop varieties launched by the government to tackle El Nino.")

def f19_forum():
    st.title("Farmer Forum")
    st.text_input("Discuss harvest prices with other farmers...")

def f20_settings():
    st.title("System Settings")
    st.toggle("WhatsApp Notifications", value=True)
    st.button("Change System Password")

# --- 6. MAIN ROUTING & POPUP LOGIC ---
def main():
    if 'is_logged_in' not in st.session_state: 
        st.session_state['is_logged_in'] = False

    is_logged = st.session_state['is_logged_in']

    # --- SIDEBAR ---
    with st.sidebar:
        if is_logged:
            user = st.session_state.get('current_user', 'Admin')
            st.markdown(f"<h2 style='text-align:center;'>Welcome, {user.capitalize()}!</h2>", unsafe_allow_html=True)
            if st.button("Logout", use_container_width=True):
                st.session_state['is_logged_in'] = False
                st.rerun()
        else:
            st.markdown("<h2 style='text-align:center;'>AgriSmart OS</h2>", unsafe_allow_html=True)
            st.write("<p style='text-align:center; color:#a99bb8; font-size:0.9rem;'>Guest Mode</p>", unsafe_allow_html=True)
            if st.button("🔐 Sign In / Register", use_container_width=True):
                login_popup() # PANGGIL POPUP DI SINI

        st.divider()
        menu = st.radio(
            "Navigation Menu",
            options=[
                "Main Dashboard", "IoT Monitor", "Irrigation Control", "AI Plant Doctor", 
                "AI Chatbot", "Fertilizer Calculator", "Market Prices", "Financials (ROI)", 
                "Weather & Climate", "Planting Calendar", "Machinery", "Warehouse Inventory", 
                "Worker Management", "Soil Quality", "Satellite Map", "Live CCTV", 
                "Pest Encyclopedia", "AgroTech News", "Farmer Forum", "Settings"
            ],
            label_visibility="collapsed"
        )

    # --- MAIN CONTENT AREA ---
    if menu == "Main Dashboard":
        # Dashboard utama boleh dilihat oleh siapa saja (Guest Mode)
        f1_dashboard()
    else:
        # Jika memilih menu lain TAPI BELUM LOGIN
        if not is_logged:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align:center;'>🔒 Access Restricted</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#a99bb8;'>This is a Premium Feature. Please sign in or create an account to continue.</p>", unsafe_allow_html=True)
            
            # Tombol darurat di tengah layar untuk memunculkan popup
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col2:
                if st.button("Sign In to Access ➔", use_container_width=True):
                    login_popup()
        
        # JIKA SUDAH LOGIN, render halamannya
        else:
            if menu == "IoT Monitor": f2_iot_monitor()
            elif menu == "Irrigation Control": f3_irrigation()
            elif menu == "AI Plant Doctor": f4_ai_doctor()
            elif menu == "AI Chatbot": f5_chatbot()
            elif menu == "Fertilizer Calculator": f6_calculator()
            elif menu == "Market Prices": f7_market_prices()
            elif menu == "Financials (ROI)": f8_financials()
            elif menu == "Weather & Climate": f9_weather()
            elif menu == "Planting Calendar": f10_calendar()
            elif menu == "Machinery": f11_machinery()
            elif menu == "Warehouse Inventory": f12_inventory()
            elif menu == "Worker Management": f13_workers()
            elif menu == "Soil Quality": f14_soil()
            elif menu == "Satellite Map": f15_satellite()
            elif menu == "Live CCTV": f16_cctv()
            elif menu == "Pest Encyclopedia": f17_encyclopedia()
            elif menu == "AgroTech News": f18_news()
            elif menu == "Farmer Forum": f19_forum()
            elif menu == "Settings": f20_settings()

if __name__ == "__main__":
    main()