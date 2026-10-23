# Auckland Property Scout — published assets

This directory holds the **generated** static build of the Auckland Property Scout
property-research app. It is copied into the assembled site by
`.github/workflows/deploy.yml` and is served at:

| Path on zhangyuqian.com | What it is |
|---|---|
| `/property-scout/` | Authored landing page (`personal-website/pages/property-scout.html`) |
| `/property-scout/app/` | Generated static app (map, market, research lab) |
| `/property-scout/app/data/snapshot.json` | Compact snapshot that the landing page hydrates from |
| `/property-scout/app/data/preview/` | Iframe posters and Open Graph cards captured by the publisher |

## Do not hand-edit `app/`

Everything under `public/property-scout/app/` is generated. It is replaced on every
publish by the research pipeline, and any manual change there will be lost.

- **Source of the app:** `Auckland Property Research/web/` (React/Vite client; static
  build mode `VITE_DATA_MODE=static`, `base: './'`).
- **Source of the data pack:** `Auckland Property Research/publish/export_pack.py`
  (writes `publish/out/data/`), copied into the app by
  `Auckland Property Research/publish/publish.py`.
- **Publisher:** `Auckland Property Research/publish/publish.py` copies the built app
  to `public/property-scout/app/` in this repo. It never touches the landing page,
  navigation, styles or scripts of this site.
- **Preview images:** `Auckland Property Research/publish/capture_previews.py` writes
  them to `publish/out/preview/`; the publisher stages them at
  `app/data/preview/` (`map-desktop.png`, `map-mobile.png`, `og-property-scout.png`, …).

The landing page is hand-authored and must not be generated:
`personal-website/pages/property-scout.html`. Its hydration script reads
`./app/data/snapshot.json` (fetch with `cache: 'no-store'`).

## Preview locally

The deployed site is assembled by the `Assemble static site with clean URLs` step in
`.github/workflows/deploy.yml`: the authored pages are rewritten into clean-URL
folders, and `public/property-scout/app/` is copied to `site/property-scout/app/`.
To preview faithfully, run that same step in a scratch copy of the repo:

```bash
cd "Personal website"                       # this repo
SCRATCH=/tmp/property-scout-site
rm -rf "$SCRATCH" && mkdir -p "$SCRATCH/public"

# Minimal repo subset the assemble step needs.
cp -R personal-website "$SCRATCH/"
cp -R public/reports public/data "$SCRATCH/public/"
cp public/CNAME "$SCRATCH/public/" 2>/dev/null || true

# Optional but recommended: a real app build + data pack, copied the way the
# research publisher will copy it. Without these, only the landing page works.
mkdir -p "$SCRATCH/public/property-scout"
cp -R ../"Auckland Property Research"/publish/out/app "$SCRATCH/public/property-scout/app"
mkdir -p "$SCRATCH/public/property-scout/app/data/preview"
cp -R ../"Auckland Property Research"/publish/out/preview/. "$SCRATCH/public/property-scout/app/data/preview/"
```

Next, extract the workflow's assemble step into a runnable script (this keeps the
rewrite rules in sync with what GitHub Pages actually runs), then serve the result:

```bash
python3 - "$SCRATCH" <<'EOF'
import pathlib, sys
lines = pathlib.Path(".github/workflows/deploy.yml").read_text().split("\n")
start = next(i for i, l in enumerate(lines) if "name: Assemble static site" in l)
run = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
block = []
for line in lines[run + 1:]:
    if line.startswith("      - ") or (line.strip() and not line.startswith("          ")):
        break
    block.append(line[10:] if line.startswith("          ") else line.lstrip())
pathlib.Path(sys.argv[1], "assemble.sh").write_text("\n".join(block) + "\n")
EOF

cd "$SCRATCH" && bash assemble.sh
cd site && python3 -m http.server 8765
# open http://127.0.0.1:8765/property-scout/
```

Notes:

- The landing page expects `./app/data/snapshot.json` (same origin). If that file or
  the `app/` build is missing, the page still renders: every measured figure stays an
  em dash and the status chip reports that the snapshot is unavailable. That fallback
  is expected behaviour, not a bug.
- The map iframe only mounts at viewports of 900px and wider, per the embed contract;
  below that the page shows the mobile poster and an "Open the live map" button.
- To test hydration against a real snapshot without a full app build, place any
  valid `snapshot.json` at `site/property-scout/app/data/snapshot.json`.

## Deployment

Push to `main` (or run the workflow manually). The workflow:

1. rewrites `../pages/property-scout.html` to `/property-scout/` in every page's
   navigation and footer links;
2. writes `site/property-scout/index.html` from the authored page;
3. copies `public/property-scout/app/` to `site/property-scout/app/` when present;
4. uploads the assembled `site/` directory to GitHub Pages.

The landing page must win over anything copied into `site/property-scout/`: its
`index.html` is written first, and the generated app lives only in the `app/`
subdirectory.
