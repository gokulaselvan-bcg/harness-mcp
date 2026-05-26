# Frontend — Tasks UI

A single-route React 18 app that consumes the Tasks API. TypeScript end-to-end,
built with Vite, Zod for runtime API-response validation, Vitest + React
Testing Library + MSW for tests.

All commands below assume you are in the `frontend/` directory.

---

## Requirements

- Node.js 18 or newer
- npm 9 or newer (bundled with Node)
- Backend running on `http://localhost:8000` (see [`../backend/README.md`](../backend/README.md))

---

## Setup

```bash
npm install
cp .env.example .env
```

The default `.env` points at the local backend:

```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Running

```bash
npm run dev
```

Vite dev server starts on `http://localhost:5173` with hot module reload.

The backend's CORS allowlist defaults to `http://localhost:5173`. If you change
the frontend port, also update `CORS_ORIGINS` in
[`../backend/.env`](../backend/.env.example).

---

## Tests, type-checking, and build

```bash
npm test            # vitest run — all tests, one shot
npm run test:watch  # vitest in watch mode

npm run typecheck   # tsc --noEmit
npm run build       # tsc --noEmit && vite build  (output in dist/)
npm run preview     # serve the production build locally
```

The test suite uses **MSW** (Mock Service Worker) to mock the API at the
network layer rather than stubbing fetch — closer to how the app behaves in
production.

---

## Environment Variables

All Vite environment variables must start with `VITE_` to be exposed to the
client. They are validated at load time by Zod
([`src/lib/env.ts`](src/lib/env.ts)) — a missing or malformed value crashes
the app immediately rather than silently producing `undefined`.

| Variable             | Default                  | Purpose                       |
|----------------------|--------------------------|-------------------------------|
| `VITE_API_BASE_URL`  | `http://localhost:8000`  | Base URL for the Tasks API    |

There are three `.env` files, one per Vite mode:

- `.env` — used by `npm run dev` and `npm run build`
- `.env.test` — used by `vitest`
- `.env.example` — checked-in template; copy to `.env` after cloning

---

## Project Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.setup.ts
└── src/
    ├── main.tsx             # React root
    ├── App.tsx              # Layout + mounts <Tasks />
    ├── vite-env.d.ts        # Vite type augmentation
    ├── lib/
    │   └── env.ts           # Zod-validated env
    └── routes/
        └── tasks/
            ├── Tasks.tsx           # Component (form, list, toggle, delete)
            ├── Tasks.test.tsx      # Component tests
            ├── tasksApi.ts         # fetch wrappers
            ├── tasksApi.test.ts    # API tests (MSW-mocked)
            └── tasksSchemas.ts     # Zod schemas + inferred types
```

---

## Conventions

- **Runtime validation at the boundary.** Every API response is parsed with a
  Zod schema before reaching the React tree. The component layer never sees
  `unknown` or unvalidated payloads.
- **No global state library.** This UI is small enough that `useState`
  suffices. Don't add Redux/Zustand unless requirements grow.
- **No CSS framework.** Inline styles are used because the component count is
  trivially small. Introduce a real styling solution before the second route.
- **Functional components only.** Hooks for state and effects.

---

## Browser support

Modern evergreen browsers (Chrome, Firefox, Safari, Edge). No IE, no
polyfills. Vite's default `esnext` target applies.
