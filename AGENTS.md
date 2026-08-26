# RelayDesk contributor guide

RelayDesk is a modular monolith control plane (`apps/web`, `supabase`) plus an independent local execution plane (`agent`). Inspect existing flows before changing architecture and do not create large unrelated refactors.

## Conventions

- Keep cloud persistence and authorization behind web API routes; never ship the service role key to browsers.
- Keep filesystem behavior in typed agent trigger/condition/action plugins. New actions implement `BaseAction`; new conditions register a small evaluator; triggers implement `BaseTrigger`.
- Validate every filesystem path. Do not add shell-command execution, implicit deletion, or arbitrary code execution.
- Business logic belongs in `lib` modules or agent services, not React components or large route handlers.
- Add tests for agent behavior using temporary directories only. Run `pytest`, web lint, type checking, and build before committing.
- Database changes must be new ordered SQL migrations, include indexes/constraints, enable RLS, and explicitly define ownership policies. Never rewrite an applied migration.
- Keep credentials out of Git and document new environment variables in `.env.example`.
