# Deployment

The initial delivery is local. No site or GitHub push was made. The static website needs neither Python nor the million-row source at runtime.

```sh
npm ci
npm run build
```

Serve `apps/web/dist` over HTTPS using any static host. A local check is `npx vite preview --config apps/web/vite.config.ts --outDir apps/web/dist --host 127.0.0.1` from the repository root, or run Vite preview from `apps/web`. Do not serve the repository root: it contains local raw/intermediate data and run evidence that must never be publicly reachable.

The app currently expects to be hosted at `/`; subpath hosting requires adjusting Vite base and absolute data/document fetch URLs before building. No client-side router fallback is needed for current anchor navigation. Keep JSON assets same-origin, declare UTF-8, and invalidate caches when updating research exports. Avoid immutable long-lived caching for the stable `research.json` alias unless the HTML is versioned with it. Check linked research Markdown and data notices after upload.

`VITE_MAP_STYLE_URL` is optional. Default is a tile-free geographic canvas with actual street lines. Any external style can request additional services; review license, quotas, attribution and user privacy. Vite environment variables are public. `VITE_REPOSITORY_URL` should point to your actual public repository after you authorize creating/pushing one; otherwise the site omits that link.

Run Python tests, types, unit tests, docs/link checks, production build and browser smoke before publishing. Keep the research-preview labels and disabled empirical layers until their evidence gates pass. Exporting `apps/web/dist` does not resolve database licensing obligations; retain [data notices](../DATA-LICENSE.md).
