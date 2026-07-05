# HyCell-JEPA 控制台

## Project One-Liner
HyCell-JEPA is a Universal-to-Specific Cellular World Model MVP for HDF aging, regeneration, and partial reprogramming.

## Current Milestone Checklist
- [x] Create project memory directories.
- [x] Create initial Codex goal files.
- [x] Create project documentation placeholders.
- [ ] Build toy single-cell perturbation dataset.
- [ ] Add gene set scoring and evidence graph.
- [ ] Implement encoders and JEPA transition core.
- [ ] Add verifier, planner, benchmark, and demo.
- [ ] Integrate real data loaders and adapters.

## Local Verification Commands
```bash
find . -maxdepth 3 -type f | sort
git status
```

Future implementation goals should also run:

```bash
pytest
```

## Daily Workflow
1. Open this control note and `docs/progress_log.md`.
2. Pick the next Codex goal from `02_Codex_Goals/`.
3. Run the goal in Codex and keep changes small enough to verify.
4. Run the goal's verification commands.
5. Update `docs/progress_log.md` and the daily note in `03_Progress/`.

## Important Principles
- Keep the toy pipeline runnable at all times.
- Do not download large datasets automatically.
- Keep configs in `configs/` and outputs in `outputs/`.
- Add tests for major modules.
- Use toy data only for engineering validation.
- Be explicit about limitations and avoid biological overclaims.
