# Deploying the Frontend to Netlify

This project uses Vite for the frontend located in the `frontend/` folder. The repository includes a `netlify.toml` and a GitHub Actions workflow to build and deploy the frontend to Netlify automatically.

Required repository secrets (GitHub):
- `NETLIFY_AUTH_TOKEN` — a Netlify personal access token (create in Netlify user settings).
- `NETLIFY_SITE_ID` — the Netlify Site ID for your site (find under Site settings > Site information).
- `VITE_API_URL` — the production API base URL (e.g. `https://api.example.com/api`).

How the workflow works:
1. On `push` to `main`, GitHub Actions runs `frontend-deploy.yml`.
2. The action installs Node, runs `npm ci`, and runs `npm run build` inside `frontend/`.
3. The built files under `frontend/dist` are deployed to Netlify via `netlify-cli` using the provided secrets.

Netlify settings (alternative to the workflow):
- You can also connect the repo directly in the Netlify UI and set the Base directory to `frontend`, Build command `npm ci && npm run build`, and Publish directory `dist`.
- Add `VITE_API_URL` under Site > Site settings > Build & deploy > Environment.

Local test/deploy steps (developer machine):
```powershell
cd frontend
npm ci
npm run build
# Preview locally if needed
npm run preview
```

Notes:
- Keep secrets out of the repository. Use the GitHub repo `Secrets` UI for `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`, and `VITE_API_URL`.
- If you prefer Netlify automatic GitHub deploys (instead of the workflow), connect the site in Netlify and it will build using `netlify.toml` automatically.
