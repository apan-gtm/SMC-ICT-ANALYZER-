import { useCallback, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Upload, Sparkles, X, Loader2, ImageIcon, Copy, Check, Crown } from "lucide-react";

const fileToBase64 = (file: File): Promise<{ base64: string; mimeType: string }> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const [meta, b64] = result.split(",");
      const mimeType = meta.match(/data:(.*?);base64/)?.[1] ?? file.type;
      resolve({ base64: b64, mimeType });
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const Index = () => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File | null) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      toast.error("File harus berupa gambar (PNG / JPG)");
      return;
    }
    if (f.size > 15 * 1024 * 1024) {
      toast.error("Ukuran maksimal 15MB");
      return;
    }
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
    setAnalysis("");
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const onPaste = (e: React.ClipboardEvent) => {
    const item = Array.from(e.clipboardData.items).find((i) => i.type.startsWith("image/"));
    if (item) {
      const f = item.getAsFile();
      if (f) {
        handleFile(f);
        toast.success("Chart berhasil di-paste");
      }
    }
  };

  const reset = () => {
    setFile(null);
    setPreviewUrl(null);
    setAnalysis("");
    setNote("");
  };

  const analyze = async () => {
    if (!file) {
      toast.error("Upload screenshot chart terlebih dahulu");
      return;
    }
    setLoading(true);
    setAnalysis("");
    try {
      const { base64, mimeType } = await fileToBase64(file);
      const { data, error } = await supabase.functions.invoke("analyze-chart", {
        body: { imageBase64: base64, mimeType, note },
      });
      if (error) throw error;
      if ((data as any)?.error) throw new Error((data as any).error);
      setAnalysis((data as any).analysis ?? "");
      toast.success("Analisa selesai");
    } catch (e: any) {
      console.error(e);
      toast.error(e?.message ?? "Gagal menganalisa chart");
    } finally {
      setLoading(false);
    }
  };

  const copyAnalysis = async () => {
    if (!analysis) return;
    await navigator.clipboard.writeText(analysis);
    setCopied(true);
    toast.success("Analisa disalin");
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="relative min-h-screen" onPaste={onPaste}>
      {/* Header */}
      <header className="relative z-10 border-b border-border/60 backdrop-blur-md bg-background/40">
        <div className="container flex items-center justify-between py-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="h-10 w-10 rounded-xl bg-gradient-gold flex items-center justify-center shadow-gold">
                <Crown className="h-5 w-5 text-primary-foreground" strokeWidth={2.5} />
              </div>
              <span className="absolute -inset-1 rounded-xl bg-primary/20 blur-md -z-10" />
            </div>
            <div>
              <h1 className="font-display text-lg font-bold tracking-tight">
                SMC <span className="text-gold-gradient">Vision</span>
              </h1>
              <p className="text-[11px] text-muted-foreground -mt-0.5 font-mono uppercase tracking-widest">
                Institutional Chart Analyst
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground font-mono">
            <span className="h-2 w-2 rounded-full bg-success animate-pulse-gold" />
            AI Online
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10 container pt-14 pb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-1.5 text-xs font-medium text-primary mb-6 animate-fade-up">
          <Sparkles className="h-3.5 w-3.5" />
          Smart Money Concept · ICT Framework
        </div>
        <h2 className="font-display text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.05] animate-fade-up">
          Analisa Chart <br />
          ala <span className="text-gold-gradient">Institusi</span>
        </h2>
        <p className="mt-5 max-w-xl mx-auto text-muted-foreground text-base sm:text-lg animate-fade-up">
          Upload screenshot chart timeframe berapapun. Dapatkan struktur market, liquidity zones,
          dan plan entry profesional dalam hitungan detik.
        </p>
      </section>

      {/* Workspace */}
      <main className="relative z-10 container pb-24">
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Upload panel */}
          <div className="card-premium rounded-2xl p-6 animate-fade-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-lg flex items-center gap-2">
                <ImageIcon className="h-4 w-4 text-primary" />
                Chart Anda
              </h3>
              {file && (
                <button
                  onClick={reset}
                  className="text-xs text-muted-foreground hover:text-destructive transition-colors flex items-center gap-1"
                >
                  <X className="h-3.5 w-3.5" /> Reset
                </button>
              )}
            </div>

            {!previewUrl ? (
              <label
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
                className={`group flex flex-col items-center justify-center text-center cursor-pointer rounded-xl border-2 border-dashed p-10 transition-all ${
                  dragOver
                    ? "border-primary bg-primary/5 scale-[1.01]"
                    : "border-border hover:border-primary/60 hover:bg-primary/[0.03]"
                }`}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                />
                <div className="h-14 w-14 rounded-2xl bg-gradient-gold flex items-center justify-center shadow-gold mb-4 group-hover:scale-110 transition-transform">
                  <Upload className="h-6 w-6 text-primary-foreground" strokeWidth={2.5} />
                </div>
                <p className="font-medium text-foreground">
                  Klik, drag & drop, atau <kbd className="font-mono text-xs bg-secondary px-1.5 py-0.5 rounded border border-border">Ctrl+V</kbd>
                </p>
                <p className="text-sm text-muted-foreground mt-1.5">
                  PNG, JPG · maks 15MB · semua timeframe (M1 – W1)
                </p>
              </label>
            ) : (
              <div className="relative rounded-xl overflow-hidden border border-border bg-black/40">
                <img
                  src={previewUrl}
                  alt="Preview chart"
                  className="w-full max-h-[460px] object-contain"
                />
              </div>
            )}

            <div className="mt-5 space-y-2">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Catatan untuk analyst (opsional)
              </label>
              <Textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Contoh: XAUUSD M15, fokus ke London session, cari setup sell."
                rows={3}
                className="bg-input/60 border-border resize-none focus-visible:ring-primary"
              />
            </div>

            <Button
              onClick={analyze}
              disabled={loading || !file}
              className="w-full mt-5 h-12 text-base font-semibold bg-gradient-gold text-primary-foreground hover:opacity-95 hover:shadow-gold transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Menganalisa likuiditas...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5 mr-2" />
                  Analisa Chart
                </>
              )}
            </Button>
          </div>

          {/* Result panel */}
          <div className="card-premium rounded-2xl p-6 animate-fade-up min-h-[400px] flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-lg flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Hasil Analisa
              </h3>
              {analysis && (
                <button
                  onClick={copyAnalysis}
                  className="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-1.5"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5" /> Tersalin
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" /> Salin
                    </>
                  )}
                </button>
              )}
            </div>

            {loading && (
              <div className="space-y-3 flex-1">
                <div className="h-4 rounded shimmer w-2/3" />
                <div className="h-4 rounded shimmer w-full" />
                <div className="h-4 rounded shimmer w-5/6" />
                <div className="h-24 rounded shimmer w-full mt-4" />
                <div className="h-4 rounded shimmer w-3/4" />
                <div className="h-4 rounded shimmer w-full" />
                <p className="text-xs text-muted-foreground font-mono pt-3">
                  ⟶ Membaca structure, liquidity & order flow...
                </p>
              </div>
            )}

            {!loading && !analysis && (
              <div className="flex-1 flex flex-col items-center justify-center text-center text-muted-foreground py-12">
                <div className="h-16 w-16 rounded-2xl border border-dashed border-border flex items-center justify-center mb-4">
                  <Sparkles className="h-7 w-7 opacity-40" />
                </div>
                <p className="font-medium text-foreground/70">Hasil analisa akan tampil di sini</p>
                <p className="text-sm mt-1 max-w-xs">
                  Format: Trend, Insight, Key Level, Plan Entry, dan Risk Reward.
                </p>
              </div>
            )}

            {!loading && analysis && (
              <article className="analysis-prose flex-1 overflow-auto pr-1">
                <ReactMarkdown>{analysis}</ReactMarkdown>
              </article>
            )}
          </div>
        </div>

        {/* Disclaimer */}
        <p className="mt-10 text-center text-xs text-muted-foreground max-w-2xl mx-auto">
          ⚠️ Analisa ini bersifat edukasi. Keputusan trading & manajemen risiko sepenuhnya tanggung
          jawab Anda. Pasar selalu memiliki ketidakpastian — gunakan stop loss.
        </p>
      </main>
    </div>
  );
};

export default Index;
