# Source documents

Ask Heinz answers only from public Heinz College and CMU documents. Both groups share one collection.

## What to collect

| Type | Examples | Owner |
| --- | --- | --- |
| Program handbooks | Each Heinz master's program handbook (current year) | Group 2 first, since the checker depends on them |
| Course catalog | Heinz course descriptions, prerequisites, units | Group 1 |
| Academic policies | Registration, pass/fail, grading, leave, credit limits | Group 1 |
| Career resources | Heinz career services pages, internship and CPT guidance | Group 1 |

Only collect pages anyone can open without logging in. Do not collect Canvas, internal portals, or anything behind Andrew ID login.

## How to store them

```
docs_corpus/
  manifest.csv     one row per document: id, title, url, type, program, date_collected
  raw/             downloaded pages and PDFs (gitignored if large)
  text/            cleaned plain text, one file per document, named by id
```

- Every document gets a row in `manifest.csv`. The `url` column is what students see as the source, so it must be the real public link.
- Refresh monthly. Handbooks change between years; record `date_collected`.
- Write the collection script once (`docs_corpus/collect.py`) so the refresh is one command.
- Respect each site's robots.txt and keep the request rate low (one page every second or two).
