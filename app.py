import streamlit as st
import google.generativeai as genai
from PIL import Image

# Setup Halaman
st.set_page_config(page_title="SMC Analyst Pro", layout="wide")
st.title("🏛️ Institusi Market Analyst (SMC/ICT)")

# API KEY KAMU (Langsung ditanam agar tidak Error)
KUNCI_API = "AIzaSyDApASwbPOnpnGkDAiflJjXA_uEfBMa-wo"

try:
    genai.configure(api_key=KUNCI_API)
    # Gunakan versi model yang paling stabil
    model = genai.GenerativeModel('gemini-1.5-flash')

    uploaded_file = st.file_uploader("Upload Chart Market", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Chart diunggah", use_container_width=True)
        
        if st.button("🚀 MULAI ANALISA INSTITUSI"):
            with st.spinner("Sabar, AI sedang membaca Liquidity..."):
                prompt = """
                Analisa chart berikut dengan gaya SMC / ICT (Smart Money Concept).
                Format WAJIB:
                📊 DAILY MACRO — [PAIR]
                Trend: (Bullish / Bearish / Sideways)
                Kondisi: (Accumulation / Manipulation / Distribution / Markup / Markdown)
                ⚠️ Insight: (Jelaskan struktur market: BOS / CHoCH, liquidity, inducement, dll)
                👉 Key Level: (Sebutkan area Demand / Supply zone dengan harga jelas)
                Skenario: (Skenario pergerakan harga selanjutnya)
                🎯 Plan Buy Limit: (harga) SL: (stop loss) TP: (target)
                🎯 Plan Sell Limit: (harga) SL: (stop loss) TP: (target)
                🚫 Hindari: (Kesalahan trader di kondisi ini)
                🧠 Kesimpulan: (Ringkasan)
                """
                response = model.generate_content([prompt, img])
                st.subheader("📋 Hasil Analisa Profesional:")
                st.write(response.text)
except Exception as e:
    st.error(f"Ada kendala: {e}")
