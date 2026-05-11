# Driver ELD Assistant — Frontend

React 19 + TypeScript + **Vite**. This app is the UI shell for the ELD assistant; most domain logic will eventually live here (trip form, map, log grid, PDF) per the [project wiki](https://github.com/aliabbas-2012/driver-eld-assistant/wiki/Requirements%E2%80%90Document).

## Scripts

```bash
npm install
npm run dev      # dev server (default http://localhost:5173)
npm run build    # production build
npm run preview  # preview production build
npm run lint
```

## API proxy

`vite.config.ts` proxies **`/api`** to **`http://127.0.0.1:8000`**, so the browser can call `/api/health/` and other endpoints while the Django server runs locally.

## Current UI

The home page fetches **`GET /api/health/`** to confirm the backend is running. Start the backend (`python manage.py runserver` from `backend/`) before relying on that check.
