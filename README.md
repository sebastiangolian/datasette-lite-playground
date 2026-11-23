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

## Makefile

```bash
make build       # build site/ (data, poland.db, self-hosted Datasette Lite at the pinned commit)
make serve       # build and serve on http://localhost:8009/ (PORT=... to change)
make test-local  # serve site/ locally and check the 9 self-hosted scenarios
make test-live   # check all 18 scenario links (both hosts) on the deployed GitHub Pages site
make clean       # remove site/ and .venv/
```

Tests (`tests/check_scenarios.py`) open each scenario link from the landing page in headless
Google Chrome via Playwright (installed into `.venv/` from `requirements-dev.txt`) and wait for
the expected data to render inside the Datasette iframe. `test-local` skips the
lite.datasette.io links: an HTTPS page cannot load data from `http://localhost`.

## Deploy

Every push to `main` runs `.github/workflows/deploy-pages.yml`, which builds the site with
`make build` and
deploys it with `actions/deploy-pages`. To update the self-hosted Datasette Lite, bump
`DATASETTE_LITE_REF`.
