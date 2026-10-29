# Deploying Jenbina to Railway

Jenbina runs on [Railway](https://railway.com) as one web service (the Streamlit
app) with a persistent volume for her memory. The app was written with Railway in
mind: the login page reads `GOOGLE_CREDENTIALS_JSON` and `REDIRECT_URI`, and every
store (ChromaDB, the SQLite user/timeline database, the time-series database)
lives under `JENBINA_DATA_DIR`, so one volume keeps all of it across deploys.

Files that drive the deploy:

| File | Purpose |
|------|---------|
| `railway.toml` | Builder (Railpack), start command, health check (`/_stcore/health`), restart policy |
| `.python-version` | Pins Python 3.11 for Railpack (matches the local venv) |
| `.railwayignore` | Keeps secrets, local databases, tests and docs out of the `railway up` upload |

The start command binds Streamlit to Railway's `$PORT` in headless mode:

```
streamlit run core/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

## The existing deployment

Jenbina already lives on Railway. The CLI in this checkout is linked to it
(`railway status` shows project, environment and service).

| | |
|---|---|
| Project | `selfless-education` (shared with the `t500` service) |
| Service | `jenbina` |
| Environment | `production` |
| URL | https://jenbina-production.up.railway.app |
| Volume | `jenbina-volume` mounted at `/jenbina`, `JENBINA_DATA_DIR=/jenbina` |
| GitHub trigger | `motya770/jenbina`, branch `main` |

All variables from the table below are already set on the service, including the
two secrets. `REDIRECT_URI` is the URL above and is registered with the Google
OAuth client.

## Deploying

From the repo root, on the branch you want live:

```bash
railway up --ci
```

`railway up` uploads the working tree (honouring `.gitignore` and `.railwayignore`),
builds it with Railpack using `railway.toml`, and streams the build logs; `--ci`
exits when the build finishes. The first build installs ChromaDB and LangChain and
takes a few minutes; later builds reuse the cache. Pushes to `main` deploy
automatically through the GitHub trigger as long as the workspace has an active
plan.

Useful commands: `railway logs` (runtime logs), `railway status`, `railway open`
(dashboard), `railway redeploy`, `railway variables` (prints values: keep it off
screenshots).

## Setting up from scratch

If the service ever has to be recreated, from the repo root:

```bash
railway login                                   # opens the browser; sign in once
railway init --name jenbina                     # creates the project and links this directory
railway add --service jenbina                   # the web service
railway service jenbina                         # link the CLI to it
railway volume add --mount-path /jenbina        # persistent disk for her memory
railway variables --set "JENBINA_DATA_DIR=/jenbina" --skip-deploys
railway domain                                  # prints the public https URL
railway variables --set "REDIRECT_URI=https://<the printed domain>" --skip-deploys
```

Set the two secrets yourself (never commit them, never paste them into chat):

```bash
railway variables --set "OPENAI_API_KEY=sk-..." --skip-deploys
railway variables --set "GOOGLE_CREDENTIALS_JSON=$(cat .google_credentials.json)" --skip-deploys
```

`GOOGLE_CREDENTIALS_JSON` is the full contents of the OAuth client JSON downloaded
from Google Cloud Console. The Variables tab of the service in the Railway
dashboard (its raw editor) works just as well.

Then allow the Railway URL in Google: Google Cloud Console → APIs & Services →
Credentials → your OAuth 2.0 Client → **Authorized redirect URIs** → add exactly the
`REDIRECT_URI` value (https, no trailing slash). Sign-in fails with `invalid_grant`
until this matches. Finish with `railway up --ci`.

## Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `OPENAI_API_KEY` | yes | Chat, embeddings, insights |
| `GOOGLE_CREDENTIALS_JSON` | yes | OAuth client JSON for Google sign-in |
| `REDIRECT_URI` | yes | The app's public URL, no trailing slash |
| `JENBINA_DATA_DIR` | yes | The volume mount path, `/jenbina` on the current service |
| `OPENAI_CHAT_MODEL` | no | Defaults from `core/connect.py` |
| `SERPAPI_API_KEY`, `SERPER_API_KEY` | no | Web search for the user dossier |
| `FIREBASE_*` | no | Set on the current service; the login page uses Google OAuth, not Firebase |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | no | Graph memory; the app runs without Neo4j |
| `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` | no | LLM tracing |
| `JENBINA_SKIP_AUTH` | no | `1` bypasses Google sign-in. **Never set it on a public URL**: anyone who finds the app could spend your OpenAI credit. |

Railway injects `PORT`; do not set it.

## Optional: Neo4j

Graph memory is optional and off until `NEO4J_URI` is set. To add it, deploy a
Neo4j template from the Railway template library into the same project
(`railway deploy -t <template code>` or the dashboard's **New → Template**), then set
`NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` on the jenbina service as
[reference variables](https://docs.railway.com/guides/variables#referencing-another-services-variable)
pointing at the Neo4j service's private URL. Neo4j Aura's free tier works too.

## Not deployed yet: the scheduler

`run_scheduler.py` runs a simulation step every few hours without the UI. It is not
part of this deploy: a Railway volume attaches to one service, and the scheduler
needs the same SQLite and ChromaDB files as the web service. The options are to run
the scheduler inside the Streamlit process, or to move the shared stores to a
network database. Until then, simulation steps run from the app's own run controls.
