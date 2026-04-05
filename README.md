# Image → PDF (Local Tool)

A lightweight local web tool to batch convert images into a single PDF — no internet required, no file size limits, no upload restrictions.

Built as a localhost Flask app that runs entirely on your machine. Open it in your browser, convert, close the terminal when done.

---

## Why local?

This tool was originally a Vercel-hosted web app but batch conversion hit Vercel's serverless request size limits. Running it locally removes all those restrictions — you can convert any number of images, any size, instantly.

---

## Stack

- **Python** + **Flask** — local server
- **img2pdf** — lossless image to PDF conversion
- **Pillow** — image processing
- Plain **HTML / CSS / JS** — no frontend framework

---

## Setup & Usage

1. Make sure **Python** is installed on your machine
2. Place `app.py` and `run.bat` in the same folder
3. Double-click `run.bat`
4. Browser opens automatically at `http://localhost:5050`
5. Add images, name your PDF, hit Convert
6. Close the terminal window when done

> First run will auto-install `flask`, `img2pdf`, and `Pillow` if not already present.

---

## Features

- Drag & drop or click to browse
- Batch convert — no limit on number of images
- Supports JPG, PNG, WEBP, BMP, TIFF
- Images numbered and listed in order before converting
- Custom PDF filename with warning if left as default
- PDF downloads straight to your Downloads folder
- Zero internet dependency after first install

---

## Files

```
├── app.py       # Flask backend + embedded frontend UI
└── run.bat      # One-click launcher (Windows)
```

---

## Author

Built by **umarJ-max**
