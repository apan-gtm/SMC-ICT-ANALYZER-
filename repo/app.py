"""
SMC Insight — Streamlit Edition
Aplikasi analisa chart trading menggunakan Smart Money Concept (SMC) & ICT framework.
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import json
from datetime import datetime

from lib.database import (
    init_db, save_analysis, get_all_history,
    get_analysis_by_id, delete_analysis
)
from lib.gemini_client import analyze_chart, fetch_news
from lib.prompts import SYSTEM_PROMPT

# ── Page config (HARUS di baris pertama setelah import) ──────────────────────
st.set_page_config(
    page_title="SMC Insight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS: dark trading terminal aesthetic ───────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');

  /* Base */
  :root {
    --bg:       #0a0d12;
    --surface:  #111620;
    --border:   #1e2a3a;
    --accent:   #00d4aa;
    --accent2:  #3b82f6;
    --warn:     #f59e0b;
    --danger:   #ef4444;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --mono:     'JetBrains Mono', monospace;
    --sans:     'Syne', sans-serif;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans);
  }

  [data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
  }

  /* Header */
  .app-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
  }
  .app-header h1 {
    font-family: var(--sans);
    font-weight: 800;
    font-size: 2rem;
    color: var(--accent);
    letter-spacing: -0.5px;
    margin: 0;
  }
  .app-header p {
    color: var(--muted);
    font-family: var(--mono);
    font-size: 0.78rem;
    margin: 0.3rem 0 0;
  }

  /* Upload box */
  [data-testid="stFileUploader"] {
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px;
    background: var(--surface) !important;
    transition: border-color 0.2s;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
  }

  /* Buttons */
  .stButton > button {
    background: var(--accent) !important;
    color: #0a0d12 !important;
    font-family: var(--mono) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.15s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }
  .stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--danger) !important;
    border: 1px solid var(--danger) !important;
    font-size: 0.75rem !important;
    padding: 0.25rem 0.6rem !important;
  }

  /* Analysis output card */
  .analysis-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 1.5rem 1.8rem;
    font-family: var(--sans);
    line-height: 1.75;
  }

  /* News card */
  .news-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.15s;
  }
  .news-card:hover { border-color: var(--accent2); }
  .news-title { font-weight: 600; font-size: 0.95rem; }
  .news-meta  { color: var(--muted); font-family: var(--mono); font-size: 0.75rem; margin-top: 0.2rem; }

  /* History item */
  .history-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.4rem;
    cursor: pointer;
    font-size: 0.82rem;
    font-family: var(--mono);
    color: var(--text);
  }
  .history-item:hover { border-color: var(--accent); }
  .history-ts { color: var(--muted); font-size: 0.7rem; display: block; margin-bottom: 2px; }

  /* Divider */
  hr { border-color: var(--border) !important; }

  /* Misc tweaks */
  .stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    font-family: var(--mono) !important;
    font-size: 0.85rem !important;
  }
  .stAlert { border-radius: 8px !important; }
  code, pre { font-family: var(--mono) !important; }
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "analysis_text": None,
    "news_data": None,
    "current_image_bytes": None,
    "current_note": "",
    "selected_history_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper: display analysis + news ──────────────────────────────────────────
def render_analysis(analysis_text: str, news_data: list | None, image_bytes: bytes | None):
    """Render analisa, chart thumbnail, dan berita."""
    col_img, col_text = st.columns([1, 2], gap="large")

    with col_img:
        if image_bytes:
            img = Image.open(BytesIO(image_bytes))
            st.image(img, use_container_width=True, caption="Chart yang dianalisa")

    with col_text:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown(analysis_text)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── News section ─────────────────────────────────────────────────────────
    if news_data:
        st.markdown("---")
        st.markdown("### 📰 Berita Terbaru")
        for item in news_data:
            title  = item.get("title", "Tanpa judul")
            source = item.get("source", "")
            date   = item.get("date", "")
            url    = item.get("url", "")
            meta   = " · ".join(filter(None, [source, date]))
            link_html = f'<a href="{url}" target="_blank" style="color:#3b82f6;">{title}</a>' if url else f'<span>{title}</span>'
            st.markdown(
                f'<div class="news-card">'
                f'<div class="news-title">{link_html}</div>'
                f'<div class="news-meta">{meta}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    elif news_data is not None:
        st.info("Tidak ada berita terbaru yang ditemukan untuk instrumen ini.")


# ── SIDEBAR: History ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕒 Riwayat Analisa")
    history_rows = get_all_history()

    if not history_rows:
        st.caption("Belum ada riwayat.")
    else:
        for row in history_rows:
            rid, created_at, preview, _ = row  # id, created_at, analysis_text[:40], news_json
            ts_label = created_at[:16] if created_at else "–"
            col_a, col_b = st.columns([4, 1])
            with col_a:
                if st.button(f"🗂 {ts_label}\n{preview}…", key=f"hist_{rid}", use_container_width=True):
                    record = get_analysis_by_id(rid)
                    if record:
                        st.session_state.current_image_bytes = record["image_bytes"]
                        st.session_state.analysis_text       = record["analysis_text"]
                        raw_news = record.get("news_json")
                        st.session_state.news_data = json.loads(raw_news) if raw_news else None
                        st.session_state.selected_history_id = rid
                        st.rerun()
            with col_b:
                if st.button("✕", key=f"del_{rid}", help="Hapus"):
                    delete_analysis(rid)
                    if st.session_state.selected_history_id == rid:
                        for k in ("analysis_text", "news_data", "current_image_bytes"):
                            st.session_state[k] = None
                        st.session_state.selected_history_id = None
                    st.toast("Analisa dihapus.", icon="🗑️")
                    st.rerun()

    st.markdown("---")
    st.caption("SMC Insight v1.0 · Powered by Gemini")


# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>📊 SMC Insight</h1>
  <p>Smart Money Concept · ICT Framework · Analisa Chart Berbasis AI</p>
</div>
""", unsafe_allow_html=True)

# ── Input section ─────────────────────────────────────────────────────────────
upload_col, ctrl_col = st.columns([2, 1], gap="large")

with upload_col:
    uploaded_file = st.file_uploader(
        "Upload screenshot chart (PNG / JPG, maks 10 MB)",
        type=["png", "jpg", "jpeg"],
        label_visibility="visible",
    )

with ctrl_col:
    note = st.text_area(
        "Catatan tambahan (opsional)",
        placeholder="mis. Saya ingin fokus ke skenario bullish, atau: pair EURUSD H4",
        height=120,
    )
    analyze_btn = st.button("🔍 Analisa Chart", use_container_width=True, type="primary")

# ── Validate & run analysis ───────────────────────────────────────────────────
if analyze_btn:
    if not uploaded_file:
        st.warning("⚠️ Silakan upload screenshot chart terlebih dahulu.")
    else:
        # Validate size (10 MB)
        file_bytes = uploaded_file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            st.error("❌ Ukuran file melebihi 10 MB. Kompres gambar lalu coba lagi.")
        else:
            # Validate & optionally resize with Pillow
            try:
                img = Image.open(BytesIO(file_bytes))
                img.verify()           # raises if corrupt
                img = Image.open(BytesIO(file_bytes))  # re-open after verify

                # Resize jika lebar > 2000px agar hemat token
                if img.width > 2000:
                    ratio = 2000 / img.width
                    img = img.resize((2000, int(img.height * ratio)), Image.LANCZOS)
                    buf = BytesIO()
                    img.save(buf, format="JPEG", quality=85)
                    file_bytes = buf.getvalue()
            except Exception as e:
                st.error(f"❌ File gambar tidak valid: {e}")
                st.stop()

            # ── Call Gemini for chart analysis ────────────────────────────
            with st.spinner("🧠 AI sedang menganalisa chart... (10–30 detik)"):
                analysis_result = analyze_chart(file_bytes, note or "")

            if analysis_result["success"]:
                analysis_text = analysis_result["text"]
                st.session_state.analysis_text       = analysis_text
                st.session_state.current_image_bytes = file_bytes
                st.session_state.news_data           = None   # reset dulu

                st.toast("✅ Analisa selesai!", icon="📊")

                # ── Fetch berita ──────────────────────────────────────────
                with st.spinner("📡 Mengambil berita terbaru..."):
                    news_result = fetch_news(analysis_text)

                news_data = news_result.get("news") if news_result.get("success") else None
                if not news_result.get("success"):
                    st.warning(f"⚠️ Berita tidak bisa diambil: {news_result.get('error', 'Unknown')}")

                st.session_state.news_data = news_data

                # ── Save to DB ────────────────────────────────────────────
                news_json = json.dumps(news_data, ensure_ascii=False) if news_data else None
                new_id = save_analysis(
                    image_bytes=file_bytes,
                    note=note or "",
                    analysis_text=analysis_text,
                    news_json=news_json,
                )
                st.session_state.selected_history_id = new_id
                st.rerun()

            else:
                error_msg = analysis_result.get("error", "Unknown error")
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.error("❌ Rate limit tercapai. Tunggu beberapa menit lalu coba lagi.")
                elif "401" in error_msg or "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                    st.error("❌ API key tidak valid. Periksa secrets.toml atau Streamlit Cloud Secrets.")
                else:
                    st.error(f"❌ Gagal analisa: {error_msg}")

# ── Display current analysis ──────────────────────────────────────────────────
if st.session_state.analysis_text:
    st.markdown("---")
    render_analysis(
        st.session_state.analysis_text,
        st.session_state.news_data,
        st.session_state.current_image_bytes,
    )
elif not analyze_btn:
    # Placeholder jika belum ada analisa
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; color:#64748b; font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
      Upload screenshot chart di atas lalu tekan <strong style="color:#00d4aa;">Analisa Chart</strong><br><br>
      Mendukung: Forex · Crypto · Saham · Indices<br>
      Timeframe: M1 hingga Monthly
    </div>
    """, unsafe_allow_html=True)
          
