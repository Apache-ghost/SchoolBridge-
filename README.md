# Project indexer

This repository contains a small index generator that scans the project and writes a JSON index file (`project-index.json`). Use it to get a quick inventory of files (paths, sizes, modification times, and SHA-1 for small files).

How to run

Open a PowerShell terminal at the repository root and run:

node .\scripts\generate-index.js

This will produce `project-index.json` in the repo root.

Notes

- The generator skips `.git`, `node_modules`, and `.vscode`.
- Files larger than 10MB won't be hashed to avoid long runtime and memory pressure.
- The generator is intentionally simple; adapt `scripts/generate-index.js` for additional metadata or filters.
