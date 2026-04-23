import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Institusi SMC/ICT Analyst", layout="wide")
st.title("🏛️ Institusi Market Analyst (SMC/ICT)")

# 2. Sidebar - Kita pakai API Key kamu yang tadi ya
with st.sidebar:
    st.header("Konfigurasi")
    # API Key yang kamu kasih saya masukkan ke sini agar kamu tidak capek input lagi
    api_key = st.text_input("Masukkan Gemini API Key:", value="AIzaSyDApASwbPOnpnGkDAiflJjXA_uEfBMa-wo", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Gunakan model gemini-1.5-flash (Tanpa v1beta di namanya agar lebih stabil)
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_file = st.file_uploader("Unggah Screenshot Chart", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            img = Image.open(uploaded_file)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(img, caption="Chart Market Real-Time", use_container_width=True)

            with col2:
                if st.button("🚀 Mulai Analisa Institusi"):
                    with st.spinner("Sedang memindai Liquidity..."):
                        prompt_expert = """
                        Analisa chart berikut dengan gaya SMC / ICT (Smart Money Concept).
                        Format WAJIB seperti ini:

                        📊 DAILY MACRO — [Sebutkan Nama PAIR/Aset]
                        Trend: (Bullish / Bearish / Sideways) 
                        Kondisi: (Accumulation / Manipulation / Distribution / Markup / Markdown)

                        ⚠️ Insight: (Jelaskan detail struktur market: BOS / CHoCH, internal/external liquidity, inducement, FVG, dan OB)

                        👉 Key Level: (Sebutkan Support / Resistance / Demand / Supply zone dengan harga jelas)

                        Skenario: (Jelaskan skenario pergerakan harga selanjutnya)

                        🎯 Plan Buy Limit: (range harga) SL: (Stop Loss) TP: (Target)
                        🎯 Plan Sell Limit: (range harga) SL: (Stop Loss) TP: (Target)

                        🚫 Hindari: (Kesalahan umum trader di kondisi ini)

                        🧠 Kesimpulan: (Ringkasan akhir + RR)
                        """
                        
                        # Memanggil AI
                        response = model.generate_content([prompt_expert, img])
                        st.subheader("📋 Laporan Analisa")
                        st.markdown(response.text)
    except Exception as e:
        # Menampilkan pesan error yang lebih jelas jika terjadi masalah teknis
        st.error(f"Waduh, ada kendala teknis: {e}")
else:
    st.warning("Masukkan API Key dulu di sebelah kiri.")
