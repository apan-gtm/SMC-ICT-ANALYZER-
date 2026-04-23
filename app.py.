import streamlit as st
import google.generativeai as genai
from PIL import Image

# Konfigurasi Halaman Web
st.set_page_config(page_title="SMC/ICT Institusi Analyst", layout="wide")

st.title("🏛️ Institusi Market Analyst (SMC/ICT)")
st.markdown("Analisa chart real-time dengan algoritma Smart Money Concept.")

# Sidebar untuk API Key
with st.sidebar:
    st.header("Konfigurasi")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    st.info("Dapatkan API Key di Google AI Studio")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Upload file gambar
    uploaded_file = st.file_uploader("Upload Screenhot Chart (TF apa saja)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(img, caption="Chart Market Real-Time", use_container_width=True)

        with col2:
            if st.button("🚀 Mulai Analisa Institusi"):
                with st.spinner("Sedang memindai Liquidity & Market Structure..."):
                    # Prompt baru sesuai permintaanmu
                    prompt_expert = """
                    Analisa chart berikut dengan gaya SMC / ICT (Smart Money Concept).
                    Format WAJIB seperti ini:

                    📊 DAILY MACRO — [Sebutkan Nama PAIR/Aset]
                    Trend: (Bullish / Bearish / Sideways) 
                    Kondisi: (Accumulation / Manipulation / Distribution / Markup / Markdown)

                    ⚠️ Insight: (Jelaskan detail struktur market secara mendalam: BOS / CHoCH, internal/external liquidity, inducement, FVG, dan OB)

                    👉 Key Level: (Sebutkan Support / Resistance / Demand / Supply zone dengan range harga yang jelas terlihat di gambar)

                    Skenario: (Jelaskan skenario pergerakan harga selanjutnya berdasarkan arah liquidity grab & structure)

                    🎯 Plan Buy Limit: (Berikan range harga entry) 
                    SL: (Stop Loss) 
                    TP: (Target 1, Target 2, dst)

                    🎯 Plan Sell Limit: (Berikan range harga entry) 
                    SL: (Stop Loss) 
                    TP: (Target 1, Target 2, dst)

                    🚫 Hindari: (Berikan peringatan kesalahan umum trader retail pada kondisi chart seperti ini)

                    🧠 Kesimpulan: (Ringkasan akhir + rasio Risk to Reward)

                    Gunakan bahasa profesional seperti analis institusi. Fokus sepenuhnya pada Price Action dan Liquidity, abaikan indikator retail biasa.
                    """
                    
                    try:
                        response = model.generate_content([prompt_expert, img])
                        st.subheader("🏛️ Hasil Analisa Profesional")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")
else:
    st.warning("Silakan masukkan API Key Anda di sidebar sebelah kiri untuk mengaktifkan AI.")
  
