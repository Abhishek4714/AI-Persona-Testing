
# SimPersona — Static Frontend (No Build Step)

This is a **fully working static frontend** for the SimPersona project.
It visualizes personas, action logs, charts, and links to mock interfaces.

## How to run (pick one)
**Option A (Python):**
```bash
cd simpersona_frontend
python -m http.server 8080
# visit http://localhost:8080
```

**Option B (VS Code):**
- Install the "Live Server" extension, right-click `index.html` → "Open with Live Server".

**Option C (Node):**
```bash
npm i -g serve
serve . -p 8080
```

> Opening `index.html` directly with `file://` may block `fetch()` due to browser security. Use a local server.

## What’s inside
- `index.html` — single-page dashboard with tabs
- `assets/js/app.js` — loads data and renders charts/tables
- `assets/css/styles.css` — styling
- `data/simpersonas.json` — personas
- `data/simpersona_actions.csv` — action logs
- `data/persona_cards/*.png` — persona card images
- `data/interfaces/*.html` — simple mock interfaces

## Tech
- Chart.js (CDN) for charts
- PapaParse (CDN) for CSV parsing
