# Final Deliverables Checklist

- Working prototype
  - Backend: `uvicorn backend.app.api.main:app --host 0.0.0.0 --port 8000 --reload`
  - Frontend: `python -m http.server 3000 --directory frontend`
  - Env: `.env` with `GROQ_API_KEY` (plus optional overrides in `backend/app/config.py`)
  - Install: `pip install -r requirements.txt` (or `make install`)
- Product brief: `docs/product_brief.md`
- Presentation deck: keep a PDF/Slides in `docs/` (add file or link)
- Demo video: 3–5 minute screencast showing end-to-end run
- Technical appendix: `docs/technical_appendix.md`

Branch note: `main` is protected; use a PR (e.g., from `cleanup` or equivalent) to merge final changes.
