# Deploying Jenbina to Railway

Jenbina runs on [Railway](https://railway.com) as one web service (the Streamlit
app) with a persistent volume for her memory. The app was written with Railway in
mind: the login page reads `GOOGLE_CREDENTIALS_JSON` and `REDIRECT_URI`, and every
store (ChromaDB, the SQLite user/timeline database, the time-series database)
lives under `JENBINA_DATA_DIR`, so one volume keeps all of it across deploys.

Files that drive the deploy:

| File | Purpose |
|------|---------|
| `railway.toml` | Builder (Railpack), start command, health check (`/_stcore/health`), restart policy; deprecated, read until the cutover |
| `.railway/railway.ts` | The same settings plus the volume, as Railway Infrastructure as Code |
| `.python-version` | Pins Python 3.11 for Railpack (matches the local venv) |
| `.railwayignore` | Keeps secrets, local databases, tests and docs out of the `railway up` upload |
| `requirements.txt` | Runtime dependencies only; test tooling lives in `requirements-dev.txt` and is not installed in production |

The start command binds Streamlit to Railway's `$PORT` in headless mode:

```
streamlit run core/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

> **`railway.toml` stops being read on 2026-12-01.** Railway has deprecated
> config-as-code files in favour of
> [Infrastructure as Code](https://docs.railway.com/infrastructure-as-code). The
> replacement is already in the repo as `.railway/railway.ts`, but it is **not
> applied yet**: until the cutover below, the service still reads `railway.toml`.
> If the cutover is skipped, the service falls back after the deadline to the start
> command stored on it and keeps starting, without the health check, the headless
> flag or the restart policy.

## Railway configuration (`.railway/railway.ts`)

`.railway/railway.ts` declares the `jenbina` service (source repo, builder, start
command, health check, restart policy) and its volume. It needs CLI 5.x
(`brew install railway`) and Railway's SDK, installed inside `.railway/` so that no
`package.json` sits at the repo root, where the builder could take the app for a
Node project:

```bash
npm install --prefix .railway --ignore-scripts
railway config plan --verbose      # read-only: shows what an apply would change
```

Rules for editing it:

- **Keep the volume declared.** The `volume("jenbina-volume", ...)` resource and the
  `volumeMounts: { "/jenbina": memory }` entry are what keep Jenbina's memory
  attached. The file `railway config migrate` generates omits both, and applying it
  that way detaches the volume. Read the plan before every apply and stop on any
  line that touches `volumeAttachments` or `jenbina-volume`.
- **Variables are unmanaged** (`variables: { managed: false }`): the file never reads
  or writes them, so secrets stay on the service only.
- The file exports `partial = "jenbina"`, so it manages this service alone and leaves
  `t500` in the same project untouched.

One-time cutover, once the workspace has an active plan (it redeploys the service):

```bash
railway config migrate cutover     # stop reading railway.toml; saves a snapshot (undo: railway config migrate undo)
railway config plan --verbose      # expect one change: health check, timeout, start command
railway config apply
```

After that, delete `railway.toml` and change settings by editing the file and running
plan and apply. Railway does not read `.railway/` during deploys.

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
`REDIRECT_URI` value (https, no trailing slash). Until this matches, sign-in fails:
Google shows `redirect_uri_mismatch`, or the app reports `invalid_grant`. Finish with `railway up --ci`.

## Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `OPENAI_API_KEY` | yes | Chat, embeddings, insights |
| `GOOGLE_CREDENTIALS_JSON` | yes | OAuth client JSON for Google sign-in |
| `REDIRECT_URI` | yes | The app's public URL, no trailing slash |
| `JENBINA_DATA_DIR` | yes | The volume mount path, `/jenbina` on the current service |
| `OPENAI_CHAT_MODEL` | no | Defaults to `openai-advanced` (`core/ui/shared_init.py`) |
| `SERPAPI_API_KEY` | no | Web search for the user dossier |
| `SERPER_API_KEY` | no | Set on the current service but read by no code; safe to delete |
| `FIREBASE_*` | no | Set on the current service; the login page uses Google OAuth, not Firebase |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | no | Graph memory; the app runs without Neo4j (see below) |
| `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` | no | LLM tracing |
| `JENBINA_SKIP_AUTH` | no | `1` bypasses Google sign-in and lets a request that names localhost open the admin panel. **Never set it on a public URL**: anyone who finds the app could spend your OpenAI credit and read the user list. |

Railway injects `PORT`; do not set it.

## Optional: Neo4j

Graph memory is optional. With `NEO4J_URI` unset the app still tries
`bolt://localhost:7687` at startup, logs one connection error, and carries on with
ChromaDB and SQLite only. To add it, deploy a
Neo4j template from the Railway template library into the same project
(`railway deploy -t <template code>` or the dashboard's **New → Template**), then set
`NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` on the jenbina service as
[reference variables](https://docs.railway.com/guides/variables#referencing-another-services-variable)
pointing at the Neo4j service's private URL. Neo4j Aura's free tier works too.

## The heartbeat on Railway

Jenbina lives continuously: the app process hosts one shared Jenbina and takes a
beat every `JENBINA_BEAT_MINUTES` (default 15) while she is awake, whether or not
anyone has the page open. Nothing extra is deployed for this; the web service is the
host. What follows from it:

- **It spends OpenAI credit around the clock.** `JENBINA_MAX_BEATS_PER_DAY` (default
  80) caps the awake beats per day. Lower it on the service to cap the cost.
- **One replica only.** A single process may host her; it takes a lease in the SQLite
  database on the volume. `.railway/railway.ts` pins one replica. Do not scale the
  service out, and do not run `run_heartbeat.py` as a second service: a Railway
  volume attaches to one service, and the second host would be refused the lease.
- **No sleeping.** Leave Railway's serverless (app sleeping) option off, or her heart
  stops whenever nobody is visiting.
- **First start adopts a saved Jenbina.** The volume already holds per-user Jenbinas
  from the February deployment. On the very first start the app adopts one of them
  as the one Jenbina: by default the real account with the most experiences, or the
  user id in `JENBINA_ADOPT_USER_ID`. This happens once.

**The Minecraft world is not part of this deploy.** `JENBINA_WORLD=minecraft` needs a
Java Minecraft server and a Node bridge beside her mind; the Railway service runs
Python only and `.railwayignore` leaves the top-level `minecraft/` folder out of the
upload. Leave `JENBINA_WORLD` unset on Railway so she lives in the described world.

The heartbeat settings (`JENBINA_BEAT_MINUTES`, `JENBINA_MAX_BEATS_PER_DAY`,
`JENBINA_LLM_TIMEOUT_SECONDS`, `JENBINA_DISABLE_SLEEP`, `JENBINA_ADOPT_USER_ID`) are
optional and described in `CLAUDE.md`.
