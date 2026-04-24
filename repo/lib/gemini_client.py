"""
lib/gemini_client.py
Wrapper untuk semua Gemini API calls menggunakan google-generativeai SDK.
"""

import re
import json
import streamlit as st
import google.generativeai as genai
from PIL import Image
from io import BytesIO

from lib.prompts import SYSTEM_PROMPT, NEWS_SYSTEM_PROMPT

VISION_MODEL = "gemini-2.0-flash"
NEWS_MODEL   = "gemini-2.0-flash"


def _configure():
    """Konfigurasi API key dari Streamlit secrets."""
    api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY tidak ditemukan di Streamlit secrets. "
            "Tambahkan di Settings → Secrets di Streamlit Cloud."
        )
    genai.configure(api_key=api_key)


def analyze_chart(image_bytes: bytes, user_note: str = "") -> dict:
    """
    Kirim gambar chart ke Gemini Vision untuk analisa SMC/ICT.
    Returns: {"success": True, "text": "..."} atau {"success": False, "error": "..."}
    """
    try:
        _configure()
        model = genai.GenerativeModel(
            model_name=VISION_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )

        img = Image.open(BytesIO(image_bytes))

        prompt = (
            f"Analisa chart ini menggunakan SMC/ICT framework.\n\nCatatan user: {user_note}"
            if user_note
            else "Analisa chart ini menggunakan SMC/ICT framework."
        )

        response = model.generate_content(
            [prompt, img],
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=3000,
            ),
        )

        return {"success": True, "text": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _extract_symbol_and_type(analysis_text: str) -> tuple:
    """Parse Symbol dan Asset Type dari teks analisa."""
    symbol_match = re.search(r"\*\*Symbol:\*\*\s*([A-Z0-9]+)", analysis_text)
    type_match   = re.search(r"\*\*Asset Type:\*\*\s*(Forex|Crypto|Stocks|Unknown)", analysis_text, re.IGNORECASE)

    symbol     = symbol_match.group(1).strip() if symbol_match else ""
    asset_type = type_match.group(1).strip()   if type_match  else ""
    return symbol, asset_type


def fetch_news(analysis_text: str) -> dict:
    """
    Ambil berita terbaru menggunakan Gemini + Google Search grounding.
    Returns: {"success": True, "news": [...]} atau {"success": False, "error": "..."}
    """
    symbol, asset_type = _extract_symbol_and_type(analysis_text)

    if not symbol or symbol.upper() == "UNKNOWN":
        return {"success": False, "error": "Symbol tidak terdeteksi dari analisa."}

    query_context = {
        "Forex":   f"{symbol} forex news today analysis",
        "Crypto":  f"{symbol} cryptocurrency news today price",
        "Stocks":  f"{symbol} stock news earnings today",
    }.get(asset_type, f"{symbol} trading news today")

    user_prompt = (
        f"Cari berita terbaru hari ini tentang {symbol} ({asset_type}). "
        f"Query: {query_context}. "
        f"Kembalikan 3–5 headline terbaru dalam format JSON yang diminta."
    )

    try:
        _configure()
        model = genai.GenerativeModel(
            model_name=NEWS_MODEL,
            system_instruction=NEWS_SYSTEM_PROMPT,
            tools="google_search_retrieval",  # Google Search grounding
        )

        response = model.generate_content(user_prompt)
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
        return {"success": False, "error": "Response berita tidak bisa di-parse sebagai JSON."}
    except Exception as e:
        return {"success": False, "error": str(e)}
