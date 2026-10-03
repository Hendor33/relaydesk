# Pokémon: První odznak

Krátká česká 2D adventura inspirovaná érou GBA. Hra běží čistě v prohlížeči v **TypeScriptu, Phaseru a Vite**; nepotřebuje účet, backend ani síťové API. Původní aplikace RelayDesk zůstává dostupná samostatným skriptem `dev:web`.

## Spuštění hry

Vyžaduje Node.js 20.19+.

```bash
npm install
npm run dev
```

Otevřete adresu vypsanou Vite (obvykle `http://localhost:5173`). Produkční verzi vytvoří `npm run build`. Pravidla herní logiky ověří `npm test`.

## Ovládání a cíl

- **WASD / šipky** – pohyb, **Z / Enter** – potvrzení a rozhovor, **X / Escape** – menu a návrat.
- Na dotykové obrazovce se zobrazí kříž a tlačítka Z/X.
- V laboratoři si zvolte startera, projděte Cestu 1 a Šeptající les, porazte tři trenéry a poté vůdce stadionu.
- Léčebna doplní HP, PP a minimální zásobu Poké Ballů. V menu lze tým prohlédnout a hru bezpečně uložit.

## Obsah a architektura

Herní data jsou oddělená od scén: `maps.ts` popisuje šest propojených lokací a NPC, `data.ts` druhy, dialogy, útoky a typovou tabulku, `state.ts` soubojová pravidla a verzované ukládání. Phaser používá samostatné scény pro titulní obrazovku, průzkum a souboj; průzkum navíc explicitně přepíná režimy dialogu a menu, takže se vstupy nepřekrývají.

Kapitola obsahuje 12 druhů, tři startery a jejich evoluce, tři trenéry, stadion, náhodná setkání pouze v trávě, tým do šesti členů a box. Uložení v `localStorage` má verzi formátu a poškozený či nedostupný save je bezpečně ignorován.

### Záměrná zjednodušení

Každý Pokémon používá jeden typový útok s 15 PP (při vyčerpání použije Zápas). Nejsou implementovány stavové efekty, IV/EV, počasí, breeding, obchodování ani multiplayer. Pokédex eviduje viděné/chycené druhy bez samostatných detailních karet. Grafika je původní procedurální pixel art tvořený Phaser primitivy, aby projekt nepoužíval cizí Pokémon assety.

---

## Původní RelayDesk

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
