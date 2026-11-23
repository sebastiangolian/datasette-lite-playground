# datasette-lite-playground

Sandbox for testing the service-worker rewrite of
[Datasette Lite](https://simonwillison.net/2026/Nov/17/datasette-lite/) — Datasette running
entirely in the browser (Pyodide + service worker).

**Live:** https://sebastiangolian.github.io/datasette-lite-playground/

The GitHub Pages site contains:

- `index.html` — clickable test scenarios, each opening either on
  [lite.datasette.io](https://lite.datasette.io/) or on the self-hosted copy under `./lite/`,
- `data/` — sample data (largest Polish cities, voivodeships) in every format Datasette Lite
  loads: SQLite (`poland.db`, built in CI), CSV, JSON, SQL script, `metadata.yml`, `datasette.yml`,
- `lite/` — a pinned commit of [simonw/datasette-lite](https://github.com/simonw/datasette-lite)
  (`DATASETTE_LITE_REF` in the workflow), with Plausible analytics removed.

GitHub Pages serves files with `Access-Control-Allow-Origin: *`, which is what Datasette Lite
needs to fetch them from another origin.

## Scenarios

| Scenario | Query string |
| --- | --- |
| SQLite + metadata + config | `?url=poland.db&metadata=metadata.yml&config=datasette.yml` |
| Canned query with parameter | `…#/poland/cities_above?min_population=300000` |
| Facets and sorting | `?url=poland.db#/poland/cities?_facet=voivodeship&_sort_desc=population` |
| Plain CSV | `?csv=cities.csv` |
| SQL schema, then CSV | `?sql=schema.sql&csv=cities.csv` |
| JSON | `?json=voivodeships.json` |
| JS plugin from PyPI | `?install=datasette-cluster-map&url=poland.db#/poland/cities` |
| Pinned versions | `?ref=stable&sqlite=3.54.1&url=poland.db#/-/versions` |
| Writes as root | `?root=1&install=datasette-write&url=poland.db#/-/write?database=poland` |

Self-hosted limitations: `?ref=<branch|commit>` and plugins installed from GitHub go through
Simon's CORS proxy, which only allows lite.datasette.io — PyPI versions and plugins work fine.
Data lives in the tab only; nothing persists across reloads.

## Running locally

```bash
mkdir -p site/data site/lite
cp index.html site/ && cp data/* site/data/
python3 scripts/build_db.py site/data/poland.db
# copy index.html, shell.js, sw.js, webworker.js from simonw/datasette-lite into site/lite/
cd site && python3 -m http.server 8009
```

Open http://localhost:8009/ (localhost is a secure context, so the service worker works).
Note that lite.datasette.io cannot load data from `http://localhost` — use the `./lite/` copy.

## Deploy

Every push to `main` runs `.github/workflows/deploy-pages.yml`, which builds the site and
deploys it with `actions/deploy-pages`. To update the self-hosted Datasette Lite, bump
`DATASETTE_LITE_REF`.
