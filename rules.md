# Rules

How entries in this collection are chosen, recorded, added and removed. The website (the Cargo pages and the map) is built from the files in `_cases/`.

## 1. What the collection is

A collection of transitional spaces (threshold sequences) in religious buildings, starting with the chapels of the Cambridge colleges. Each entry records the sequence of spaces a visitor passes through and how one space changes into the next.

## 2. Scope

| layer | scope |
|---|---|
| `college-chapel` | Chapels of the Cambridge colleges (23 of the 31 colleges have one) |
| `cambridge-other` | Other religious buildings in Cambridge, e.g. Great St Mary's, theological college chapels, the Leper Chapel, Cambridge Central Mosque |
| `cambridgeshire` | Religious buildings elsewhere in Cambridgeshire, e.g. Ely Cathedral |

## 3. Inclusion criteria

An entry is included when it meets **at least one** of:
- the building itself carries an idea of threshold;
- its architect, or published writing on it, describes this transition explicitly;
- the transition has a recognised cultural or ritual meaning;

and **both** of:
- it has a clear sequence of open and enclosed spaces (open–enclosed–open or enclosed–open–enclosed);
- at least one property (height, width, light, material) changes visibly between consecutive spaces, and this can be documented from drawings, published descriptions or site visits.

For the `cambridge-other` and `cambridgeshire` layers, candidates are found by taking every `amenity=place_of_worship` in OpenStreetMap within the area, then applying the criteria above.

## 4. One file per building

Each file in `_cases/` describes one building. A building can have several routes (`sequences`); each route is a list of spaces (`segments`) in the order they are walked.

## 5. Codes

| layer | prefix | example |
|---|---|---|
| `college-chapel` | C | C01 |
| `cambridge-other` | K | K01 |
| `cambridgeshire` | E | E01 |

A code is never changed or reused.

## 6. Tags

Use only these words; add a new one here before using it. Names follow the sources (RCHME, listing descriptions, college publications).

- `screen`: timber or metal screen
- `arch`: arch or doorway in a wall
- `vestibule`: small lobby between screens
- `octagonal-ante-chapel`
- `crossing`: crossing under a tower
- `ascent`: vertical rise along the route
- `side-route`: a parallel route beside the main one

## 7. Fields

See `_cases/C01-kings-college-chapel.md`.

Required: `code` `name` `layer` `published` `lat` `lon` `coord_source` `sources`.
Optional: `college` `built` `dimensions` `osm` `osm_site` `chapel_page` `cargo_url` `tags` `sequences` `images`.

- Coordinates come from OpenStreetMap (`osm` holds the OSM object, e.g. `way/123456`; `osm_site` holds the college or site boundary). If another source is used for now, say so in `coord_source`.
- Give dimensions in the units of the source, followed by metres (1 ft = 0.3048 m).
- Put the construction dates in `built`. **Do not use a field called `date`**: GitHub Pages reads it as a publication date and the site fails to build.
- No personal email addresses: this repository is public. Link to the college's own page instead.
- `images` lists every image shown on the entry's page. Each item has `view` (one of `context`, `plan`, `section`, `axo`, `photos` — the five tabs on the page), `caption`, `author`, `license` and `url`. The full working list, with the Cargo media hashes, is `data/manifest.json`; `tools/update_case_images.py` rewrites the `images` blocks from it.

## 8. Images and sources

- Every image needs an author, year, source link and licence. Images without licence information are not used.
- Wikimedia Commons images are credited according to their licence (e.g. CC BY-SA 4.0).
- RCHME (1959) plates: British History Online's reuse terms are still to be checked, so these are linked, not shown.
- Own photographs and sketches: "© Haining Ding".
- Site plans are drawn from OpenStreetMap with `tools/siteplan.js` (building black, college buildings mid grey, context light grey, site boundary dashed) and credited "© OpenStreetMap contributors (ODbL)".
- Historical drawings: Willis & Clark, *The Architectural History of the University of Cambridge* (1886), Atkinson & Clark, *Cambridge Described and Illustrated* (1897), Loggan (1690), Britton (1807), Le Keux (c. 1840) — all public domain, taken from the scans on Wikimedia Commons / Internet Archive.
- Drawing legend: thick line = wall in section; thin line = edge in view; dash-dot line = route; T1, T2… = threshold positions.

## 9. Adding and removing entries

- **Add**: copy a file in `_cases/`, rename it `code-name.md`, fill in the fields, set `published: true`, commit. The map adds the point automatically.
- **Remove from the site**: set `published: false`. The file stays in the repository.
- **Change these rules**: edit this file and add a line to the change log below.

## Change log

- 2026-10-25: First version.
- 2026-10-25: Construction-date field renamed from `date` to `built`.
- 2026-10-25: English only; project-internal fields removed.
- 2026-10-26: Added C02–C23 and K01–K10 (OSM coordinates, site plans, Commons images); `osm_site` field added. Tags and routes for these entries are still to be filled in.
- 2026-10-26: Pages reorganised into five views (Context, Plan, Section, Axonometric, Photographs); `images` items gain a `view` field; plans, sections and historical views added from Willis & Clark (1886), Atkinson & Clark (1897), Britton (1807) and others.
