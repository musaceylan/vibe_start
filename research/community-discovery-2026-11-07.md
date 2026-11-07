# Community and ecosystem discovery — 2026-11-07

Targeted GitHub search for gaps in the skill supply chain, config portability, skill evaluation and secrets. Metadata and READMEs only; nothing was executed. Star counts are weak evidence: several repositories show implausible growth. Candidates are queued only. Every gate in `manifests/curation-policy.json` is still open, and activation needs human approval.

## Queued candidates

| Repository | Gap | Check during curation |
|---|---|---|
| `FiloSottile/age` | Encrypted backup of secrets when switching machines | Key custody and recovery |
| `twpayne/chezmoi` | Same gap, with templating and native age support | Overlap with vibe_backup's sync and install scripts |
| `NVIDIA/SkillSpector` | Static skill scanning with SARIF output and baselines | Compare with `snyk/agent-scan`; keep one gate. Needs Python 3.12+ |
| `agentskills/agentskills` | `skills-ref` tooling for the Agent Skills specification | Needs Python 3.11+ |
| `microsoft/waza` | Skill behaviour evals; `vibe benchmark` only measures routing | Compare with `claude plugin eval` first; confirm a standalone arm64 build |
| `dyoshikawa/rulesync` | One source for Codex, Kimi, Qwen and other provider configs | Adopt only if it replaces `configure-agents.py` |
| `DeusData/codebase-memory-mcp` | Local code graph | Benchmark against Serena and existing code intelligence |

## Reviewed and not queued

- `ruvnet/ruflo`: competing global control plane.
- `vectorize-io/hindsight`, `topoteretes/cognee`, `volcengine/OpenViking`: overlap the memory layer; OpenViking is AGPL-3.0.
- `Paritok-official/paritok-4b-v1`, `ojuschugh1/sqz`: context interception requires a controlled benchmark before any activation.
- `FailproofAI/failproofai`: license is not identified by GitHub.
- Large skill collections: no unique capability.

## Upstream security advisories

Published GitHub advisories were read for all 81 catalogued repositories, except the private `musaceylan/claude-security-skills` mirror (the API refused it). Pins moved past advisories in this pass:

- `garrytan/gstack` to 1.96.0.0 in vibe_backup (GHSA-249x-w96r-pw6c, fixed in 1.91.159.0).
- `jarrodwatts/claude-hud` to 0.15.0 (GHSA-fq7j-8hxj-jfqh, GHSA-25hg-g83m-4w35, GHSA-f7gq-pcm8-rxr4).
- `ast-grep/ast-grep` to 0.51.1 (GHSA-xx6h-xcfw-vf5j, GHSA-cmvf-x8f7-rvp6).

Unpinned on-demand tools must be taken at or above these fixed versions: `oraios/serena` 2.0.0, `ChromeDevTools/chrome-devtools-mcp` 1.5.0, `aquasecurity/trivy` 0.71.1, `headroomlabs-ai/headroom` 0.35.0.
