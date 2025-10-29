# Replit Flask Scraper (Ready-to-Upload)

This repo exposes a tiny `/scrape` endpoint that fetches ESPN college-football homepage and returns a sample of headlines.

## How to use on Replit (2025 UI)

**Path A — Import ZIP (fastest)**

1. From the Replit dashboard left sidebar, click **Import code or design**.
2. Choose **Upload ZIP**, select this zip file.
3. Once the editor opens, confirm files: `main.py`, `requirements.txt`.
4. Click **Run** (top). When the preview opens, click **Open in new tab** and visit `/scrape`.
   - Example: `https://<your-app>.<region>.replit.app/scrape`
5. Optional: Add secrets via left sidebar **Secrets** (🔑). Add `CFB_API_KEY` if needed.

**Path B — Create Blank App, then paste files**

1. Left sidebar → **Apps** → **New app** → **Blank app** → **Python**.
2. Create files: `main.py`, `requirements.txt` with the contents from this repo.
3. Click **Run**, open `/scrape` as above.

## Deploy (to keep it live)
1. Left sidebar → **Deployments** → **Create Deployment**.
2. Type: **Autoscale** (cheap) or **Reserved VM** (always-on).
3. Start command: `python main.py`.
4. Add any env vars (secrets) in the Deployment settings.
5. Publish and use the production URL from the deployment.

## Endpoints
- `/scrape` → returns JSON payload with `headlines_sample`.
- `/health` → returns `{ ok: true }` for uptime checks.
