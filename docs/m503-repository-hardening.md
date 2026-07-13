# M5.0.3 — Repository Hardening and Public Asset CLI

M5.0.3 closes the asset-pipeline milestone.

## Public command

```bash
uv run g2a assets PACKAGE \
  --output DIRECTORY \
  [--ace-root DIRECTORY] \
  [--force]
```

`g2stack dev` remains the orchestration command and invokes asset conversion
automatically.

## Repository hygiene

CI runs `scripts/check-repository-hygiene.sh`. The check rejects patch files,
pre-migration backups, delivery notes, implementation scratch notes, rejected
merge files, and placeholder tests.
