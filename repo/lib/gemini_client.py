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

# ── Model constants ───────────────────────────────────────────────────────────
VISION_MODEL = "gemini-2.0-flash-exp"
NEWS_MODEL   = "gemini-2.0-flash-exp"

# ── Lazy client init ──────────────────────────────────────────────────────────
@st.cache_resource
def _get_client() -> "genai.Client":
    """Buat Gemini client sekali, cache di session Streamlit."""
    api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY tidak ditemukan di Streamlit secrets. "
            "Tambahkan di .streamlit/secrets.toml atau Streamlit Cloud Settings → Secrets."
        )
    return genai.Client(api_key=api_key)


# ── Chart analysis ────────────────────────────────────────────────────────────
def analyze_chart(image_bytes: bytes, user_note: str = "") -> dict:
    """
    Kirim gambar chart ke Gemini Vision untuk analisa SMC/ICT.

    Returns:
        {"success": True, "text": "..."}
        {"success": False, "error": "..."}
    """
    try:
        client = _get_client()

        # Encode gambar ke base64
        img_b64   = base64.standard_b64encode(image_bytes).decode("utf-8")
        mime_type = "image/jpeg"  # Pillow sudah normalize ke JPEG jika di-resize

        # Bangun pesan user
        user_parts = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
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

        return {"success": True, "text": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Parse Symbol from analysis text ──────────────────────────────────────────
def _extract_symbol_and_type(analysis_text: str) -> tuple[str, str]:
    """
    Parse Symbol dan Asset Type dari teks analisa.
    Returns (symbol, asset_type) — keduanya string kosong jika tidak ditemukan.
    """
    symbol_match = re.search(r"\*\*Symbol:\*\*\s*([A-Z0-9]+)", analysis_text)
    type_match   = re.search(r"\*\*Asset Type:\*\*\s*(Forex|Crypto|Stocks|Unknown)", analysis_text, re.IGNORECASE)

    symbol     = symbol_match.group(1).strip() if symbol_match else ""
    asset_type = type_match.group(1).strip()   if type_match  else ""
    return symbol, asset_type


# ── News fetch via Google Search grounding ────────────────────────────────────
def fetch_news(analysis_text: str) -> dict:
    """
    Ambil 3–5 headline berita terbaru menggunakan Gemini + Google Search grounding.

    Returns:
        {"success": True, "news": [...]}
        {"success": False, "error": "..."}
    """
    symbol, asset_type = _extract_symbol_and_type(analysis_text)

    if not symbol or symbol.upper() == "UNKNOWN":
        return {"success": False, "error": "Symbol tidak terdeteksi dari analisa."}

    # Buat query kontekstual
    query_context = {
        "Forex":   f"{symbol} forex news today analysis",
        "Crypto":  f"{symbol} cryptocurrency news today price analysis",
        "Stocks":  f"{symbol} stock news earnings today",
    }.get(asset_type, f"{symbol} trading news today")

    user_prompt = (
        f"Cari berita terbaru hari ini tentang {symbol} ({asset_type}). "
        f"Query: {query_context}. "
        f"Kembalikan 3–5 headline terbaru dalam format JSON yang diminta."
    )

    try:
        client = _get_client()

        response = client.models.generate_content(
            model=NEWS_MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=NEWS_SYSTEM_PROMPT,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
                max_output_tokens=1500,
            ),
        )

        raw = response.text.strip()

        # Strip markdown fence jika ada
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$",          "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        news_list = json.loads(raw)
        if not isinstance(news_list, list):
            news_list = []

        return {"success": True, "news": news_list}

    except json.JSONDecodeError:
        # Gemini kadang return teks bukan JSON murni — fallback graceful
        return {"success": False, "error": "Response berita tidak bisa di-parse sebagai JSON."}
    except Exception as e:
        return {"success": False, "error": str(e)}
