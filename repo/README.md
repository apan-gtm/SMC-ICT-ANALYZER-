# 📊 SMC Insight — Streamlit Edition

Aplikasi analisa chart trading berbasis **Smart Money Concept (SMC)** dan **ICT (Inner Circle Trader)** framework, didukung **Google Gemini 2.5 Pro** dengan vision dan Google Search grounding untuk berita real-time.

---

## ✨ Fitur

| Fitur | Keterangan |
|---|---|
| 🔍 Analisa Chart | Upload screenshot → Gemini Vision menganalisa SMC/ICT secara lengkap |
| 📰 Berita Real-Time | Auto-fetch headline terbaru menggunakan Google Search grounding |
| 🕒 Riwayat Analisa | Simpan & buka kembali analisa sebelumnya (gambar + teks + berita) |
| 🌑 Dark UI | Terminal-style dark theme, mobile-friendly |

---

## 🚀 Setup Lokal

### 1. Clone repo
```bash
git clone https://github.com/USERNAME/smc-insight-streamlit.git
cd smc-insight-streamlit
```

### 2. Buat virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Dapatkan Gemini API Key

1. Buka [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Login dengan akun Google
3. Klik **"Create API key"**
4. Salin key yang dihasilkan

### 5. Buat file secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIza..."   # ← paste API key kamu di sini
```

> ⚠️ File `secrets.toml` sudah di-`.gitignore`. **Jangan pernah commit file ini.**

### 6. Jalankan aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`

---

## ☁️ Deploy ke Streamlit Community Cloud

### Langkah-langkah:

1. **Push ke GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Buka [share.streamlit.io](https://share.streamlit.io)**

3. **Klik "New app"** → pilih repo & branch → set Main file path: `app.py`

4. **Set Secrets:**
   - Di dashboard app → klik **"Settings"** → **"Secrets"**
   - Paste:
     ```toml
     GEMINI_API_KEY = "AIza..."
     ```
   - Klik **Save**

5. **Klik "Deploy"** — aplikasi live dalam 1–2 menit!

> **Catatan storage:** Streamlit Cloud tidak memiliki persistent storage. Riwayat analisa disimpan di `/tmp/history.db` dan akan hilang saat app restart/sleep. Untuk persistent history di cloud, pertimbangkan integrasi Supabase atau Google Cloud Storage (pengembangan lanjutan).

---

## 📁 Struktur Project

```
smc-insight-streamlit/
├── app.py                        # Entry point Streamlit
├── lib/
│   ├── __init__.py
│   ├── gemini_client.py          # Analisa chart + fetch berita
│   ├── database.py               # SQLite CRUD
│   └── prompts.py                # System prompts
├── .streamlit/
│   ├── config.toml               # Dark theme config
│   └── secrets.toml.example      # Template secrets
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🛠️ Troubleshooting

### ❌ `Error 429 — Resource exhausted`
**Penyebab:** Rate limit Gemini API (terutama tier gratis).  
**Solusi:**
- Tunggu 1–2 menit lalu coba lagi.
- Upgrade ke Gemini API paid tier di [Google AI Studio](https://aistudio.google.com).
- Kurangi frekuensi analisa.

### ❌ `Error 401 — API key not valid`
**Penyebab:** API key salah atau belum aktif.  
**Solusi:**
- Pastikan key di `secrets.toml` benar (tidak ada spasi ekstra).
- Generate ulang key di [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
- Di Streamlit Cloud: pastikan sudah save di **Settings → Secrets**.

### ❌ `Upload gagal / File terlalu besar`
- Maksimum ukuran: **10 MB**.
- Kompres gambar di [squoosh.app](https://squoosh.app) atau tool lain.
- Gunakan format JPEG (lebih kecil dari PNG untuk chart).

### ❌ `ModuleNotFoundError: google.genai`
```bash
pip install google-genai
```
Pastikan menggunakan `google-genai` (SDK baru), **bukan** `google-generativeai` (SDK lama).

### ❌ `Berita tidak muncul`
- Fitur berita menggunakan Google Search grounding yang memerlukan koneksi internet.
- Jika Symbol di analisa tidak terdeteksi (`Unknown`), berita tidak akan diambil.
- Pastikan analisa menyebutkan Symbol dengan jelas.

### ❌ Riwayat hilang setelah deploy ulang
- Normal di Streamlit Cloud (storage ephemeral di `/tmp`).
- Untuk persistent history: integrasikan database cloud (Supabase, Firebase, dll).

---

## 🔒 Keamanan

- **Jangan pernah** commit `secrets.toml` ke Git.
- API key hanya berjalan di server-side — tidak terekspos ke browser.
- Gambar yang diupload hanya disimpan di memori dan DB lokal, tidak dikirim ke pihak ketiga selain Gemini API.

---

## 📝 Lisensi

MIT License — bebas digunakan dan dimodifikasi.

---

*Built with ❤️ using Streamlit + Google Gemini*
