# Architecture

## Boundaries

The **control plane** is the Vercel-hosted Next.js application backed by Supabase Auth/PostgreSQL. It owns users, devices, declarative automation definitions, execution history, and logs. The **execution plane** is the user-owned Python process. It alone watches and changes local files. Vercel never hosts a permanent watcher.

Automations are reusable ordered primitives: one trigger, zero or more conditions, and ordered actions. JSON configuration is validated in both the web API and agent models. This relational-plus-JSON representation can map directly to a future node editor without changing runtime semantics.

## Pairing and authentication

An authenticated user asks `/api/pairing` for a short random code. Only its SHA-256 hash is stored, with a 10-minute expiry and owner. The agent exchanges it once at `/api/agent/pair`; an atomic database function consumes it and creates a device plus random credential. Only a credential hash is persisted. Subsequent agent requests send `Authorization: Bearer <credential>` and `X-Device-ID`; server routes hash and authenticate these values before accessing data with the server-only Supabase client.

## Runtime

The agent reconciles enabled automation definitions on startup and periodically, replacing watcher registrations when definitions change. (The polling path is the reliable fallback and MVP synchronization mechanism; Realtime can later be added as a low-latency hint.) A watchdog event is deduplicated, checked for stable size, converted to an execution context, and handed to the engine. The engine creates an execution, evaluates conditions, runs actions in position order, updates the shared context after each action, and always reports terminal success or failure. Reporting and heartbeat calls retry temporary network errors with bounded exponential backoff.

Paths are absolute, must not contain traversal segments, and destination directories must already exist. RelayDesk exposes only explicit file actions and never invokes a shell or automatically deletes a file.

## Deployment

Apply migrations with the Supabase CLI (`supabase db push`). Configure the three variables in `.env.example` in Vercel, choose `apps/web` as the root directory, and deploy. The application is stateless; Supabase remains the source of truth.
