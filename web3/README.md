# Web3Hunt — artex-ko, specialized for live smart-contract hunting

Fork of [jiwoochris/artex-ko](https://github.com/jiwoochris/artex-ko) (AGPL-3.0,
license retained in full; this overlay documents every change below).

## What this is

The upstream project is a general security-agent harness. This branch turns one
running instance into a **live Web3 0-day hunter**: it finds never-exploited,
currently-at-risk smart contracts, proves exploits with fork PoCs, and builds
rescue/disclosure packets — across hooks, lending, perps, bridges, vaults,
oracles, governance, routers, and paid bounty scopes. Methodology includes the
Veria/XRPL chained-low playbook (pair every low with its guarding check).

## What changed (the whole overlay is `web3/`)

- `web3/skills/web3-contract-audit/` — audit skill: SKILL.md workflow, 7
  references (bug-catalog A–M, evm-checklist, v4-hooks, chains/RPCs/explorers,
  bounty-intake, rescue-ops, chained-lows), triage script.
- `web3/tools/*.json` — 7 custom tool definitions (foundry hint, JSON-RPC read,
  contract call, storage, calldata decode, tx trace, explorer fetch, v4 PoolId).
- `web3/mission/hunt.json` — the hunt mission: never-exploited scope, hard
  exclusion list, evidence bar, 9 seeded sub-goals.
- `web3/mission/llm-profiles.json` — free-model gateway profile specs.
- `web3/setup-web3hunt.py` — provisions a FRESH instance (profiles → skill →
  tools → mission) with zero clicks. No secrets inside: gateway keys are local
  dummy values.
- No upstream source files were modified by this overlay.

## Run a second (web3) instance next to the default one

```powershell
Copy-Item artex.exe web3hunt.exe
.\web3hunt.exe -addr :8790 -data .\web3hunt-data -proxy ""
# read the first-run token from stdout, save it, then:
python web3/setup-web3hunt.py --base http://localhost:8790 --token <token>
```

Keep the default instance on `:8787`. Do not share `-data` dirs between
instances. Free-model gateways are slow — one active hunter per tier at a time.

## Compliance

AGPL-3.0 applies to the whole tree including this overlay. If you distribute a
modified binary, ship the corresponding source (this branch) with it.
