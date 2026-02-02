import streamlit as st
import google.generativeai as genai
import PIL.Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AgriSmart Online",
    page_icon="🌾",
    layout="centered"
)

# --- 1. KEAMANAN API KEY (LOGIKA DEPLOYMENT) ---
# Kita tidak menaruh key langsung disini agar tidak dicuri orang di GitHub.
# Kita mengambilnya dari "Brankas Rahasia" (Secrets) milik Streamlit Cloud.
try:
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    else:
        # Fallback jika dijalankan lokal tapi belum setting secrets.toml
        st.error("⚠️ API Key tidak ditemukan di Secrets!")
        st.info("Jika dijalankan lokal, buat file .streamlit/secrets.toml")
        st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan konfigurasi: {e}")
    st.stop()

# Konfigurasi Google AI dengan Key yang aman
genai.configure(api_key=api_key)

# --- 2. FUNGSI LOGIKA UTAMA ---
def main():
    st.title("🌾 AgriSmart Vision (Online)")
    st.caption("Sistem Pakar Pertanian Berbasis AI & Computer Vision")

    # Sidebar Login
    with st.sidebar:
        st.header("🔐 Login Akses")
        # Di versi online, sebaiknya password agak rumit dikit
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        login_btn = st.button("Masuk Sistem")
        
        if login_btn:
            if username == "admin" and password == "petanisukses2026":
                st.session_state['is_logged_in'] = True
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Kombinasi User/Pass salah!")
    
    # Cek Session State
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    # Tampilkan konten berdasarkan status login
    if st.session_state['is_logged_in']:
        tampilan_dashboard_petani()
    else:
        st.info("👋 Silahkan login di menu sebelah kiri untuk mengakses layanan.")
        st.markdown("""
        **Info Akun Demo:**
        * User: `admin`
        * Pass: `petanisukses2026`
        """)

# --- 3. TAMPILAN CHATBOT & VISION ---
def tampilan_dashboard_petani():
    st.divider()
    
    # Gunakan model Flash Latest (Gratis & Cepat)
    model = genai.GenerativeModel("gemini-flash-latest")

    # Tombol Logout
    if st.button("Keluar / Logout"):
        st.session_state['is_logged_in'] = False
        st.rerun()

    # History Chat
    if "history_chat" not in st.session_state:
        st.session_state.history_chat = []

    # Render History
    for chat in st.session_state.history_chat:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])
            # Jika ada gambar di history (opsional, logic sederhana disini hanya text)
    
    # --- FITUR UPLOAD FOTO ---
    with st.expander("📸 Upload Foto Tanaman (Opsional)", expanded=False):
        uploaded_file = st.file_uploader("Pilih foto daun/hama...", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, caption="Preview Gambar", width=250)
            st.success("Foto siap dianalisa AI")

    # --- INPUT USER ---
    user_input = st.chat_input("Jelaskan masalah tanaman Anda...")

    if user_input:
        # 1. Tampilkan pertanyaan user
        with st.chat_message("user"):
            st.write(user_input)
            if uploaded_file:
                st.image(uploaded_file, width=200)
        
        st.session_state.history_chat.append({"role": "user", "content": user_input})

        # 2. Proses AI
        with st.spinner("Sedang menganalisa data pertanian..."):
            try:
                # Siapkan prompt
                system_prompt = "Kamu adalah ahli pertanian. Jawablah dengan ringkas dan solutif. "
                final_input = [user_input]
                
                # Jika ada gambar, masukkan ke list input
                if uploaded_file:
                    img = PIL.Image.open(uploaded_file)
                    final_input.append(img)
                    system_prompt += "Analisa gambar ini untuk mendeteksi penyakit/hama. "

                # Gabungkan prompt sistem (manual trick) + input user
                # Catatan: gemini-flash-latest kadang lebih patuh jika instruksi digabung di prompt
                
                response = model.generate_content(final_input)
                ai_reply = response.text

                # 3. Tampilkan Jawaban
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                
                st.session_state.history_chat.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"Terjadi kendala koneksi: {e}")

if __name__ == "__main__":
    main()