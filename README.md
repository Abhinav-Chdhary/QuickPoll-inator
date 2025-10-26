# QuickPoll-inator
Real-Time Opinion Polling Platform

## Run the project locally

This repo has two apps:

- `quick-poll-inator/` — Next.js frontend
- `backend/` — FastAPI backend

### Prerequisites

- Python 3.10+ (with `pip`)
- Node.js 18+ (LTS recommended) and npm

---

### Backend (FastAPI)

Path: `backend/`

1. Create and activate a virtual environment

   macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server (hot-reload)
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   - API base URL: `http://localhost:8000/`
   - API docs (Swagger): `http://localhost:8000/docs`

Notes:

- CORS is open for local development in `backend/main.py`.
- `.env` exists at `backend/.env` (currently empty). Add environment variables here if/when needed.

---

### Frontend (Next.js)

Path: `quick-poll-inator/`

1. Install dependencies
   ```bash
   npm install
   ```

2. Start the dev server
   ```bash
   npm run dev
   ```

   - App URL: `http://localhost:3000/`

Optional:

- If the frontend needs to call the backend, ensure it targets `http://localhost:8000`. If you introduce an env var, you can add something like `NEXT_PUBLIC_API_BASE=http://localhost:8000` to a `.env.local` in `quick-poll-inator/` and consume it in your API client.

---

### Running both together

- Start the backend first on port 8000.
- Start the frontend on port 3000 in a separate terminal.

Ports used by default:

- Backend: `8000`
- Frontend: `3000`

If these ports are busy, change the port in the respective start command (`--port` for uvicorn or `-p` for Next.js, e.g. `next dev -p 3001`).
