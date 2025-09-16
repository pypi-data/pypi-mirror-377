# Frontend Dev API usage

This template includes a tiny API client (api.ts) that abstracts calls under the single-origin dev server:

- Real platform endpoints (when `hla-compass dev --online` is used) via `/api/...`:
  - `apiGet(path)` / `apiPost(path, body)`
- Local-only dev endpoints via `/dev/...` or module actions under `/api/...`:
  - `devGet(path)` / `devPost(path, body)`

Examples:

```ts path=null start=null
import { apiGet, devPost } from './api';

// Execute module locally (dev server)
const result = await devPost('/execute', { input: { param1: 'demo' } });

// Fetch real API data (proxied when online mode is enabled)
const samples = await apiGet('/data/alithea-bio/immunopeptidomics/samples?page=1&limit=5&data_source=alithea-hla-db');
```

Notes:
- All calls are same-origin (no CORS issues) because `/api` and `/dev` are served by the dev server.
- Real API proxying requires `hla-compass dev --online` with a valid login.
- TLS verification is enforced; if your local trust store needs a bundle, start dev with `--ca-bundle /path/to/ca.pem`.
