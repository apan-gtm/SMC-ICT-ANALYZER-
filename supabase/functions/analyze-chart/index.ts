// Edge function: analyze trading chart with SMC/ICT framework using Lovable AI (Gemini vision)
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SYSTEM_PROMPT = `Anda adalah analis institusi profesional yang menguasai Smart Money Concept (SMC) dan ICT (Inner Circle Trader). Analisa chart yang diberikan dengan fokus pada LIQUIDITY, market structure, dan order flow — BUKAN indikator biasa (RSI, MACD, MA, dll).

Anda WAJIB membalas HANYA dalam format markdown berikut, persis seperti template, dengan bahasa Indonesia profesional:

📊 DAILY MACRO — [PAIR / TIMEFRAME]

**Trend:** (Bullish / Bearish / Sideways)
**Kondisi:** (Accumulation / Manipulation / Distribution / Markup / Markdown)

⚠️ **Insight**
(Jelaskan struktur market: BOS / CHoCH, liquidity sweep, inducement, order block, FVG, mitigasi, dll. Sebutkan di mana likuiditas mayor berada.)

👉 **Key Level**
- Support / Demand zone: (harga jelas)
- Resistance / Supply zone: (harga jelas)
- Liquidity pool: (harga jelas)

**Skenario:**
(Skenario pergerakan harga berdasarkan liquidity & structure — bullish & bearish path)

🎯 **Plan**
- Buy/Sell Limit: (range harga)
- SL: (stop loss)
- TP1: (target 1)
- TP2: (target 2)
- TP3: (opsional)

🚫 **Hindari**
(Kesalahan umum trader retail di kondisi ini — chasing price, FOMO entry tanpa konfirmasi BOS, dll)

🧠 **Kesimpulan**
(Ringkasan singkat + Risk:Reward ratio yang ditawarkan setup ini.)

ATURAN:
- Identifikasi pair & timeframe dari chart jika terlihat. Jika tidak terbaca, tulis "Tidak teridentifikasi".
- Gunakan harga AKTUAL dari chart, jangan mengarang angka.
- Jangan menyebut indikator klasik. Fokus liquidity, structure, order flow.
- Jangan tambahkan disclaimer panjang di luar template.`;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const { imageBase64, mimeType, note } = await req.json();
    if (!imageBase64) {
      return new Response(JSON.stringify({ error: "imageBase64 wajib diisi" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) throw new Error("LOVABLE_API_KEY tidak terkonfigurasi");

    const dataUrl = `data:${mimeType || "image/png"};base64,${imageBase64}`;
    const userText = note?.trim()
      ? `Analisa chart ini dengan framework SMC/ICT. Catatan tambahan dari trader: ${note}`
      : "Analisa chart ini dengan framework SMC/ICT.";

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-pro",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          {
            role: "user",
            content: [
              { type: "text", text: userText },
              { type: "image_url", image_url: { url: dataUrl } },
            ],
          },
        ],
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate limit tercapai. Coba lagi sebentar." }),
          { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );
      }
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: "Credits habis. Tambahkan kredit di Settings → Workspace → Usage." }),
          { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );
      }
      const t = await response.text();
      console.error("AI gateway error:", response.status, t);
      return new Response(JSON.stringify({ error: "Gagal menganalisa chart" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    const analysis = data?.choices?.[0]?.message?.content ?? "";

    return new Response(JSON.stringify({ analysis }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("analyze-chart error:", e);
    return new Response(
      JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
