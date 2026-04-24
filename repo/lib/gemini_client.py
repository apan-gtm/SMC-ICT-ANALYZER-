"""
lib/gemini_client.py
Wrapper untuk semua Gemini API calls:
  - analyze_chart()  : analisa chart image dengan vision
  - fetch_news()     : ambil berita via Google Search grounding
"""

import re
import json
import base64
import streamlit as st

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "Package 'google-genai' tidak ditemukan. "
        "Jalankan: pip install google-genai"
    )

from lib.prompts import SYSTEM_PROMPT, NEWS_SYSTEM_PROMPT

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)


# ── Model constants (DIUBAH KE VERSI YANG BENAR) ──────────────────────────────
# Gunakan gemini-2.0-flash-exp untuk fitur terbaru & tercepat
VISION_MODEL = "gemini-3-flash-preview"
NEWS_MODEL   = "gemini-3-flash-preview"

# ── Lazy client init ──────────────────────────────────────────────────────────
@st.cache_resource
def _get_client() -> "genai.Client":
    """Buat Gemini client sekali, cache di session Streamlit."""
    # Mengambil key dari Streamlit secrets
    api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY tidak ditemukan. Pastikan sudah diisi di .streamlit/secrets.toml"
        )
    return genai.Client(api_key=api_key)


# ── Chart analysis ────────────────────────────────────────────────────────────
def analyze_chart(image_bytes: bytes, user_note: str = "") -> dict:
    """
    Kirim gambar chart ke Gemini Vision untuk analisa SMC/ICT.
    """
    try:
        client = _get_client()

        # Bangun pesan user menggunakan format SDK google-genai terbaru
        user_parts = [
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(
                text=f"Analisa chart ini menggunakan SMC/ICT framework.\n\nCatatan user: {user_note}"
                if user_note
                else "Analisa chart ini menggunakan SMC/ICT framework."
            ),
        ]

        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[types.Content(role="user", parts=user_parts)],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=3000,
            ),
        )

        if not response.text:
            return {"success": False, "error": "Gemini tidak memberikan respon teks."}

        return {"success": True, "text": response.text}

    except Exception as e:
        return {"success": False, "error": f"Gagal analisa: {str(e)}"}


# ── Parse Symbol from analysis text ──────────────────────────────────────────
def _extract_symbol_and_type(analysis_text: str) -> tuple[str, str]:
    """
    Parse Symbol dan Asset Type dari teks analisa hasil output Gemini.
    """
    # Regex untuk mencari **Symbol:** NamaAsset
    symbol_match = re.search(r"\*\*Symbol:\*\*\s*([A-Z0-9/._-]+)", analysis_text)
    type_match   = re.search(r"\*\*Asset Type:\*\*\s*(Forex|Crypto|Stocks|Indices|Unknown)", analysis_text, re.IGNORECASE)

    symbol     = symbol_match.group(1).strip() if symbol_match else ""
    asset_type = type_match.group(1).strip()   if type_match  else ""
    return symbol, asset_type


# ── News fetch via Google Search grounding ────────────────────────────────────
def fetch_news(analysis_text: str) -> dict:
    """
    Ambil headline berita terbaru menggunakan Gemini + Google Search grounding.
    """
    symbol, asset_type = _extract_symbol_and_type(analysis_text)

    if not symbol or symbol.upper() == "UNKNOWN":
        return {"success": False, "error": "Symbol tidak terdeteksi dari teks analisa."}

    # Buat query pencarian yang spesifik
    query_context = {
        "Forex":   f"{symbol} currency pair news analysis today",
        "Crypto":  f"{symbol} crypto price news today live",
        "Stocks":  f"{symbol} stock market news earnings",
    }.get(asset_type, f"{symbol} trading news analysis today")

    user_prompt = (
        f"Berikan 3-5 berita fundamental terbaru hari ini tentang {symbol} ({asset_type}). "
        f"Gunakan Google Search. Kembalikan HANYA dalam format JSON list of objects: "
        f"[{{'title': '...', 'source': '...', 'url': '...', 'impact': 'High/Med/Low'}}] "
    )

    try:
        client = _get_client()

        # Memanggil Gemini dengan tools Google Search
        response = client.models.generate_content(
            model=NEWS_MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=NEWS_SYSTEM_PROMPT,
                tools=[types.Tool(google_search=types.GoogleSearch())], # Aktifkan Search
                temperature=0.2,
            ),
        )

        raw = response.text.strip()

        # Membersihkan markdown (```json ... ```) jika ada
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$",          "", raw, flags=re.MULTILINE)
        
        news_list = json.loads(raw)
        return {"success": True, "news": news_list}

    except json.JSONDecodeError:
        return {"success": False, "error": "Format berita dari AI bukan JSON yang valid."}
    except Exception as e:
        return {"success": False, "error": f"Gagal ambil berita: {str(e)}"}
