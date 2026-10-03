# RelayDesk

RelayDesk is a personal automation platform with a Next.js/Supabase control plane and a lightweight Python execution agent. The first vertical slice watches a local folder, filters files by extension, moves matching files, and reports executions and logs.

## Repository

- `apps/web` – Next.js App Router dashboard and authenticated API routes
- `agent` – independently packaged Python CLI and automation runtime
- `supabase/migrations` – schema, pairing RPCs, indexes, and row-level security
- `docs/architecture.md` – control/execution plane design and request flows

## Quick start

### Supabase

1. Create a Supabase project and run `supabase db push` (or apply files in `supabase/migrations` in order).
2. Copy `.env.example` to `apps/web/.env.local` and provide the project URL, anon key, and server-only service role key.
3. Enable email/password authentication. Never expose the service role key with a `NEXT_PUBLIC_` prefix.

### Web

```bash
npm install
npm run dev
```

Open http://localhost:3000, create an account, then create a device pairing code from **Devices**. Deploy `apps/web` to Vercel; set the same three environment variables in the Vercel project.

### Agent

Python 3.11+ is required.

```bash
cd agent
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
relaydesk-agent pair
relaydesk-agent start
```

`pair` asks for the web URL and one-time code. Credentials are saved with user-only permissions in the platform configuration directory. `start` reconciles automations periodically (30 seconds by default), watches folders, and sends heartbeats. Run `relaydesk-agent doctor` for diagnostics.

## Validation

```bash
npm run lint
npm run typecheck
npm run build
cd agent && pytest
```

See `.env.example` for configuration and `docs/architecture.md` for security and operational details.
