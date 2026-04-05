from flask import Flask, request, send_file, render_template_string
import img2pdf
import io
import os
from PIL import Image

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image → PDF</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0d0d0d;
    --surface: #141414;
    --border: #222;
    --accent: #00ff88;
    --accent-dim: rgba(0,255,136,0.12);
    --text: #e8e8e8;
    --muted: #555;
    --danger: #ff4444;
    --warn: #ffaa00;
    --warn-dim: rgba(255,170,0,0.10);
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 300;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 24px;
  }

  header { text-align: center; margin-bottom: 48px; }

  h1 { font-size: 32px; font-weight: 300; letter-spacing: -0.5px; line-height: 1.2; }
  h1 span { color: var(--accent); font-weight: 500; }

  .subtitle {
    margin-top: 8px;
    font-size: 13px;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 32px;
    width: 100%;
    max-width: 640px;
  }

  .section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  .hint {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 14px;
    line-height: 1.6;
  }

  .drop-zone {
    border: 1px dashed var(--muted);
    border-radius: 2px;
    padding: 44px 32px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
    position: relative;
  }

  .drop-zone.drag-over {
    border-color: var(--accent);
    background: var(--accent-dim);
  }

  .drop-zone input[type="file"] {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
    width: 100%;
    height: 100%;
  }

  .drop-icon { font-size: 28px; margin-bottom: 10px; display: block; color: var(--muted); }

  .drop-text { font-size: 14px; color: var(--muted); line-height: 1.7; }
  .drop-text strong { color: var(--text); font-weight: 500; }
  .drop-text small { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #3a3a3a; }

  .file-list {
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .file-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .file-count {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--accent);
  }

  .clear-all {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    background: none;
    border: none;
    cursor: pointer;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    transition: color 0.1s;
  }
  .clear-all:hover { color: var(--danger); }

  .file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 12px;
    background: #0d0d0d;
    border: 1px solid var(--border);
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
  }

  .file-item .fnum { color: #333; margin-right: 10px; min-width: 18px; }
  .file-item .fname { color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
  .file-item .fsize { color: var(--muted); flex-shrink: 0; margin-left: 10px; font-size: 11px; }

  .remove-btn {
    background: none;
    border: none;
    color: var(--muted);
    cursor: pointer;
    font-size: 16px;
    padding: 0 0 0 10px;
    line-height: 1;
    flex-shrink: 0;
    transition: color 0.1s;
  }
  .remove-btn:hover { color: var(--danger); }

  .divider { height: 1px; background: var(--border); margin: 28px 0; }

  .filename-block { display: flex; flex-direction: column; gap: 8px; }

  .filename-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .filename-input {
    flex: 1;
    background: #0d0d0d;
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    padding: 10px 12px;
    border-radius: 2px;
    outline: none;
    transition: border-color 0.15s;
  }

  .filename-input:focus { border-color: var(--accent); }
  .filename-input.is-default { border-color: var(--warn); }

  .pdf-ext {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: var(--muted);
    flex-shrink: 0;
  }

  .filename-warn {
    display: none;
    background: var(--warn-dim);
    border: 1px solid rgba(255,170,0,0.25);
    border-radius: 2px;
    padding: 8px 12px;
    font-size: 12px;
    color: var(--warn);
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.6;
  }

  .filename-warn.visible { display: block; }
  .filename-hint { font-size: 12px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }

  .convert-btn {
    width: 100%;
    padding: 14px;
    background: var(--accent);
    color: #000;
    border: none;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: opacity 0.15s;
    margin-top: 4px;
  }

  .convert-btn:hover { opacity: 0.85; }
  .convert-btn:disabled { opacity: 0.3; cursor: not-allowed; }

  .status {
    margin-top: 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    text-align: center;
    min-height: 18px;
  }

  .status.ok { color: var(--accent); }
  .status.err { color: var(--danger); }
  .status.working { color: var(--muted); }

  footer {
    margin-top: 48px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .footer-credit {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #333;
    letter-spacing: 0.12em;
  }

  .footer-credit a {
    color: var(--accent);
    text-decoration: none;
    opacity: 0.7;
    transition: opacity 0.15s;
  }

  .footer-credit a:hover { opacity: 1; }

  .footer-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #2a2a2a;
    letter-spacing: 0.08em;
  }
</style>
</head>
<body>

<header>
  <h1>Image <span>→</span> PDF</h1>
  <p class="subtitle">// batch convert · runs on your machine</p>
</header>

<div class="card">

  <div class="section-label">Step 1 — Add your photos</div>
  <p class="hint">Drop all the images you want to merge into one PDF. You can add JPG, PNG, WEBP, BMP or TIFF files — as many as you need. They'll be combined in the order shown below.</p>

  <div class="drop-zone" id="dropZone">
    <input type="file" id="fileInput" accept="image/*" multiple>
    <span class="drop-icon">⊕</span>
    <p class="drop-text">
      <strong>Click here or drag & drop your images</strong><br>
      <small>JPG · PNG · WEBP · BMP · TIFF &nbsp;—&nbsp; no limit on how many</small>
    </p>
  </div>

  <div class="file-list" id="fileList"></div>

  <div class="divider"></div>

  <div class="section-label">Step 2 — Name your PDF file</div>
  <p class="hint">Give your PDF a meaningful name so you can find it easily later. The file will be saved to your Downloads folder.</p>

  <div class="filename-block">
    <div class="filename-row">
      <input type="text" class="filename-input" id="filename" value="output" placeholder="e.g. invoice-march, scan-001, report">
      <span class="pdf-ext">.pdf</span>
    </div>
    <div class="filename-warn" id="filenameWarn">
      ⚠ &nbsp; Rename this before converting — it will save as <strong>output.pdf</strong> by default.
    </div>
    <span class="filename-hint" id="filenameHint" style="display:none">✓ will be saved as: <span id="filenamePreview"></span>.pdf</span>
  </div>

  <div class="divider"></div>

  <button class="convert-btn" id="convertBtn" disabled onclick="convert()">
    Convert to PDF
  </button>

  <div class="status" id="status"></div>
</div>

<footer>
  <div class="footer-credit">built by <span style="color:var(--accent)">Umar J</span></div>
  <div class="footer-note">running locally · close the terminal to stop</div>
</footer>

<script>
  let files = [];

  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const convertBtn = document.getElementById('convertBtn');
  const status = document.getElementById('status');
  const filenameInput = document.getElementById('filename');
  const filenameWarn = document.getElementById('filenameWarn');
  const filenameHint = document.getElementById('filenameHint');
  const filenamePreview = document.getElementById('filenamePreview');

  filenameInput.addEventListener('input', updateFilenameUI);

  function updateFilenameUI() {
    const val = filenameInput.value.trim();
    if (!val || val === 'output') {
      filenameInput.classList.add('is-default');
      filenameWarn.classList.add('visible');
      filenameHint.style.display = 'none';
    } else {
      filenameInput.classList.remove('is-default');
      filenameWarn.classList.remove('visible');
      filenameHint.style.display = 'block';
      filenamePreview.textContent = val;
    }
  }

  // don't show warning on load, only after user interacts

  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    addFiles([...e.dataTransfer.files]);
  });

  fileInput.addEventListener('change', () => addFiles([...fileInput.files]));

  function addFiles(newFiles) {
    newFiles.forEach(f => {
      if (f.type.startsWith('image/') && !files.find(x => x.name === f.name && x.size === f.size)) {
        files.push(f);
      }
    });
    renderList();
    fileInput.value = '';
  }

  function removeFile(i) {
    files.splice(i, 1);
    renderList();
  }

  function clearAll() {
    files = [];
    renderList();
  }

  function renderList() {
    fileList.innerHTML = '';
    if (files.length === 0) {
      convertBtn.disabled = true;
      convertBtn.textContent = 'Convert to PDF';
      status.textContent = '';
      status.className = 'status';
      return;
    }

    const header = document.createElement('div');
    header.className = 'file-list-header';
    header.innerHTML = `<span class="file-count">${files.length} image${files.length > 1 ? 's' : ''} queued</span><button class="clear-all" onclick="clearAll()">Clear all</button>`;
    fileList.appendChild(header);

    files.forEach((f, i) => {
      const div = document.createElement('div');
      div.className = 'file-item';
      div.innerHTML = `<span class="fnum">${String(i+1).padStart(2,'0')}</span><span class="fname">${f.name}</span><span class="fsize">${(f.size/1024).toFixed(0)} KB</span><button class="remove-btn" onclick="removeFile(${i})">×</button>`;
      fileList.appendChild(div);
    });

    convertBtn.disabled = false;
    convertBtn.textContent = `Convert ${files.length} image${files.length > 1 ? 's' : ''} → PDF`;
    status.textContent = '';
    status.className = 'status';
  }

  async function convert() {
    if (!files.length) return;
    updateFilenameUI();
    if (filenameInput.value.trim() === '' || filenameInput.value.trim() === 'output') {
      filenameInput.focus();
      return;
    }
    convertBtn.disabled = true;
    status.className = 'status working';
    status.textContent = `processing ${files.length} files...`;

    const fd = new FormData();
    files.forEach(f => fd.append('images', f));
    fd.append('filename', filenameInput.value.trim() || 'output');

    try {
      const res = await fetch('/convert', { method: 'POST', body: fd });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Server error');
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const fname = filenameInput.value.trim() || 'output';
      a.href = url;
      a.download = fname.endsWith('.pdf') ? fname : fname + '.pdf';
      a.click();
      URL.revokeObjectURL(url);
      status.className = 'status ok';
      status.textContent = `✓ done — ${files.length} image${files.length > 1 ? 's' : ''} merged`;
    } catch(e) {
      status.className = 'status err';
      status.textContent = '✕ ' + e.message;
    } finally {
      convertBtn.disabled = false;
    }
  }
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/convert", methods=["POST"])
def convert():
    images = request.files.getlist("images")
    if not images:
        return {"error": "No images received"}, 400

    filename = request.form.get("filename", "output")

    processed = []
    errors = []

    for img_file in images:
        try:
            img = Image.open(img_file.stream).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            buf.seek(0)
            processed.append(buf.read())
        except Exception as e:
            errors.append(f"{img_file.filename}: {str(e)}")

    if not processed:
        return {"error": "Failed to process images: " + "; ".join(errors)}, 400

    pdf_bytes = img2pdf.convert(processed)
    pdf_buf = io.BytesIO(pdf_bytes)
    pdf_buf.seek(0)

    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ").strip() or "output"
    if not safe_name.endswith(".pdf"):
        safe_name += ".pdf"

    return send_file(
        pdf_buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=safe_name
    )

if __name__ == "__main__":
    import webbrowser, threading
    def open_browser():
        import time; time.sleep(1)
        webbrowser.open("http://localhost:5050")
    threading.Thread(target=open_browser).start()
    app.run(port=5050, debug=False)
