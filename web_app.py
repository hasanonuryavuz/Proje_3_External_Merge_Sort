from flask import Flask, request, render_template_string, send_file
from pathlib import Path
import tempfile
import csv
import time
from main import external_sort

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>External Merge Sort</title>
<style>
* {box-sizing:border-box}
body {
 margin:0; font-family:Segoe UI,Arial,sans-serif;
 background:#0f172a; color:#f8fafc;
}
.container {max-width:900px;margin:45px auto;padding:20px}
.subtitle {color:#a5b4fc;font-size:13px;font-weight:bold}
h1 {font-size:36px;margin:12px 0}
.muted {color:#94a3b8}
.panel {
 background:#1e293b;padding:28px;
 border-radius:16px;margin-top:25px;
}
label {display:block;margin:18px 0 9px;font-weight:600}
input {
 width:100%;padding:14px;border-radius:9px;
 border:1px solid #475569;background:#0f172a;color:white;
}
button,.download {
 display:block;width:100%;margin-top:25px;
 padding:16px;background:#6366f1;color:white;
 border:0;border-radius:10px;font-size:16px;
 font-weight:bold;cursor:pointer;text-align:center;
 text-decoration:none;
}
button:hover,.download:hover {background:#4f46e5}
.stats {
 display:grid;grid-template-columns:repeat(3,1fr);
 gap:15px;margin-top:22px;
}
.stat {background:#334155;padding:20px;border-radius:12px}
.stat span {color:#cbd5e1;font-size:13px}
.stat h2 {margin:10px 0 0}
.success {
 color:#86efac;background:#14532d;
 padding:15px;border-radius:9px;margin-top:20px;
}
.error {color:#fecaca;background:#7f1d1d;padding:15px;border-radius:9px}
.footer {text-align:center;margin-top:35px;color:#64748b;font-size:12px}
@media(max-width:600px) {
 .stats {grid-template-columns:1fr}
 h1 {font-size:27px}
}
</style>
</head>
<body>
<div class="container">
 <div class="subtitle">PROJE 3 | PYTHON & FLASK</div>
 <h1>External Merge Sort</h1>
 <p class="muted">Dışsal Bellek Tabanlı Büyük Dosya Sıralayıcısı</p>

 <div class="panel">
  <h2>CSV Dosyası Sıralama</h2>
  <p class="muted">Başlıksız, tek sütunlu tam sayı CSV dosyası seçin. Yükleme sınırı 100 MiB.</p>
  <form action="/sort" method="post" enctype="multipart/form-data">
   <label>Girdi CSV Dosyası</label>
   <input type="file" name="file" accept=".csv" required>
   <label>Blok Boyutu (Satır)</label>
   <input type="number" name="chunk_size" value="10000"
          min="1" max="1000000" required>
   <button type="submit" id="start">▶ SIRALAMAYI BAŞLAT</button>
  </form>

  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}

  {% if result %}
  <div class="success">✓ Sıralama başarıyla tamamlandı!</div>
  <div class="stats">
   <div class="stat"><span>TOPLAM SATIR</span><h2>{{ result.rows }}</h2></div>
   <div class="stat"><span>PARÇA SAYISI</span><h2>{{ result.parts }}</h2></div>
   <div class="stat"><span>İŞLEM SÜRESİ</span><h2>{{ result.seconds }} sn</h2></div>
  </div>
  <p class="muted">Geçici dosyalar otomatik temizlendi.</p>
  <a class="download" href="/download/{{ result.token }}">
    ↓ SIRALANMIŞ CSV DOSYASINI İNDİR
  </a>
  {% endif %}
 </div>
 <div class="footer">External Merge Sort • Python • heapq.merge</div>
</div>
<script>
document.querySelector("form").addEventListener("submit",function(){
 const btn=document.getElementById("start");
 btn.disabled=true;
 btn.innerText="⏳ SIRALANIYOR...";
});
</script>
</body>
</html>
"""

OUTPUT_DIR = Path(tempfile.gettempdir()) / "external_merge_sort_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.errorhandler(413)
def too_large(error):
    return render_template_string(HTML, error="Dosya yükleme sınırı 100 MiB."), 413


@app.get("/")
def home():
    return render_template_string(HTML)


@app.post("/sort")
def sort_file():
    from uuid import uuid4

    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename.lower().endswith(".csv"):
        return render_template_string(
            HTML, error="Lütfen bir CSV dosyası seçin."
        ), 400

    try:
        chunk_size = int(request.form.get("chunk_size", "10000"))
        if not 1 <= chunk_size <= 1_000_000:
            raise ValueError("Blok boyutu 1 ile 1000000 arasında olmalı.")

        token = uuid4().hex
        output = OUTPUT_DIR / f"{token}.csv"

        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.csv"
            uploaded.save(input_path)
            result = external_sort(input_path, output, chunk_size)

        result["token"] = token
        return render_template_string(HTML, result=result)

    except (ValueError, UnicodeError, csv.Error) as error:
        if "output" in locals():
            output.unlink(missing_ok=True)
        return render_template_string(HTML, error=str(error)), 400


@app.get("/download/<token>")
def download(token):
    from uuid import UUID
    from flask import abort

    try:
        UUID(hex=token)
    except ValueError:
        abort(404)

    path = OUTPUT_DIR / f"{token}.csv"
    if not path.is_file():
        abort(404)

    return send_file(
        path, as_attachment=True,
        download_name="sirali_sonuc.csv",
        mimetype="text/csv"
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)