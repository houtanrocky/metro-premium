# Deployment

The static site runs without Python or the private source data. Deploy only `apps/web/dist`; never serve the repository root, private source cache or run directories.

## GitHub Pages

The GitHub Actions workflow in [.github/workflows/ci.yml](../.github/workflows/ci.yml) runs the Python, React, TypeScript, documentation and browser checks. Only a successful `main` build can deploy. It builds with the Pages base path, tests the resulting production site in English and Persian on desktop/mobile, uploads only the distribution directory, and deploys through the `github-pages` environment. Pull requests run validation without publishing.

In the repository's **Settings → Pages**, use **GitHub Actions** as the build source. The workflow uses revision-pinned actions and the minimum Pages deployment permissions. Raw inputs, private runs and review files are excluded from Git and deployment artifacts.

To reproduce a project-site build in PowerShell:

```powershell
npm ci
$env:VITE_BASE_PATH='/metro-premium/'
$env:VITE_REPOSITORY_URL='https://github.com/houtanrocky/metro-premium'
npm run build
node scripts/check-pages.mjs
```

For root hosting, use `/` as `VITE_BASE_PATH`. No client-side router fallback is needed for anchor navigation. Asset and download paths use the configured base, including map workers and fonts.

English links use `?lang=en`; Persian links use `?lang=fa`. Explicit links take priority over the saved language; first visits otherwise default to Persian. The language switch updates document direction, metadata, controls, dates and numbers. Authored UI text lives in `apps/web/src/locales/en.json` and `fa.json`; research exports retain their original scientific content. Source identifiers, original research documents and exported technical charts remain in their source language.

`VITE_MAP_STYLE_URL` is optional. The default loads the actual small street extract without external map tiles. Review attribution and privacy before choosing an external style. All `VITE_` values are public browser configuration, so never use them for secrets. Retain the [data notices](../DATA-LICENSE.md) and font license.

The preview labels, historical-network caveats and disabled operational metro layers remain in both languages. Publishing software does not approve a scientific finding.
