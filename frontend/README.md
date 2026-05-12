# Driver ELD Assistant — Frontend

React 19 + Vite + **Tailwind CSS v4** + **Leaflet** (`react-leaflet`) + **Axios**.

## Scripts

```bash
npm install
npm run dev
npm run build
```

## Environment

| Variable | Purpose |
|----------|---------|
| (dev) | Vite proxies `/api` → `http://127.0.0.1:8000` |
| `VITE_API_BASE_URL` | Production only: full API origin, e.g. `https://api.example.com` (requests go to `$VITE_API_BASE_URL/api/...`) |

## Vercel

- Root directory: **`frontend`**
- Build: **`npm run build`**
- Output: **`dist`**
- Set **`VITE_API_BASE_URL`** to your deployed Django base URL.

## UI

Login → trip form (current / pickup / dropoff / cycle used / start date) → **Plan** loads map + per-day log sheets (table + canvas grid from `log_grid_data`).
