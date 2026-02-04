# ProductMaker Website

This folder contains the ProductMaker app UI (chatbot, folder tree, editor, app viewer, and agent workflow).

## Run locally

```bash
npm install
npm run dev
```

## Environment

Set the API base URL if the backend is not on the default `http://localhost:8080`.

```bash
export VITE_API_BASE_URL=http://localhost:8080
```

The backend expects these env vars:

- `FRONTEND_BASE_URL` (default `http://localhost:5173`)
- `CORS_ALLOWED_ORIGINS` (comma-separated)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`
- `OAUTH_REDIRECT_BASE` (default `http://localhost:8080`)
- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_SUCCESS_URL` / `STRIPE_CANCEL_URL`
- `STRIPE_WEBHOOK_SECRET` (optional)
- `FREE_USAGE_LIMIT` (default `5`)
- `SESSION_TTL_SECONDS` (default `86400`)
