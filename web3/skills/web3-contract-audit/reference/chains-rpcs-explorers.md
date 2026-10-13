# Chains, RPCs, Explorers — reference

Use the RPC of the chain the target is deployed on. Public RPCs are rate-limited/flaky — retry, and
prefer a working one. `cast` verbs take `--rpc-url <RPC>`.

## Public RPCs (fallback order — status verified 2026-10-10 from our network)
| Chain | id | RPC |
|-------|----|-----|
| Ethereum | 1 | `https://ethereum-rpc.publicnode.com`, `https://eth.llamarpc.com`, `https://rpc.ankr.com/eth` (all three 403ing as of 2026-10-10 — retry, or use a keyed provider) |
| Base | 8453 | `https://base.gateway.tenderly.co` (WORKS, no key; `eth_getLogs` capped at **1000 blocks/call** — chunk; `cast run`/historical state limited) |
| Arbitrum One | 42161 | `https://arb1.arbitrum.io/rpc` (403ing as of 2026-10-10) |
| Optimism | 10 | `https://mainnet.optimism.io` (WORKS) |
| Polygon | 137 | `https://polygon-rpc.com` (401 as of 2026-10-10) |
| BNB Chain | 56 | `https://bsc-dataseed.binance.org` (WORKS) |
| Robinhood Chain | 4663 | `https://rpc.mainnet.chain.robinhood.com` (403ing as of 2026-10-10) |

Note: `cast run` (fork trace) and `cast storage`/historical `eth_getLogs` need an **archive node**;
most public RPCs are not archive. For deep historical traces use an archive provider (Alchemy/Infura/
QuickNode) or `forge test --fork-url` with an archive URL.

## Explorer source / ABI APIs
- **Blockscout v2**: `GET {explorer}/api/v2/smart-contracts/{addr}` (source, ABI, proxy info);
  `GET {explorer}/api/v2/addresses/{addr}` (balances, txs); logs: `?module=logs&action=getLogs`.
- **Etherscan v2 (unified, key required)**: `GET https://api.etherscan.io/v2/api?chainid={id}&module=contract&action=getsourcecode&address={addr}&apikey={key}`;
  same host for all chains with `chainid`. Also `getabi`, `getlogs`, `txlist`.
- **Sourcify**: `GET https://repo.sourcify.dev/contracts/full_match/{chain}/{addr}/` (verified metadata+source).
- If the explorer page is Cloudflare-protected, use the browser tool, not raw curl.

## Uniswap v4 (PER-CHAIN deployments — the 0x0000 address is NOT universal)
- Ethereum: PoolManager `0x000000000004444c5dc75cB358380D2e3dE08A90`.
- **Base: PoolManager `0x498581fF718922c3f8e6A244956aF099B2652b2b` (24,009 bytes, verified live), PositionManager `0x7C5f5A4bBd8fD63184577525326123B519429bDc`.** Do NOT use the 0x0000 address on Base — it is empty there.
- Always confirm the PM address on-chain (`eth_getCode` nonzero) before scanning a new chain.
- Base PM quirk (verified 2026-10-10): `getLiquidity(bytes32)` (0xfa6793d5) **reverts** on this deployment — do not rely on it. Use `extsload` (0x1e2eaeaf) for state reads, or rank pools by Swap-event volume / ModifyLiquidity sums instead.
- `Initialize` topic0: `0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438` (non-indexed data: fee[0:64] tickSpacing[64:128] **hooks[128:192]** sqrtPrice[192:256] tick[256:320] — hook address is the LAST 20 bytes of the third word).
- `Swap` topic0: `0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f`.
- `getHookPermissions()` selector: `0xc4e833ce`.
- Tenderly gateway quirks (verified 2026-10-12, all cost worker turns to learn):
  `eth_getCode` can return `0xef` for a live contract (cross-check with a view
  call); `trace_call`/`debug_traceCall` exist but 429 under any load — design
  tests around logs + return values; anvil forks work but EVERY launch spawns a
  process — kill stale `anvil` before each run; agent shell is PowerShell
  (`;` chains, no `&&`) and foundry is NOT on PATH (full path
  `C:\Users\stagh\.foundry\bin` or prepend per command).

## Useful cast verbs
- `cast code <addr> --rpc-url <RPC>` — runtime bytecode.
- `cast storage <addr> <slot> --rpc-url <RPC>` — raw storage (1967 impl slot: `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a9c30c58fd9bf`).
- `cast call <addr> "<sig>" [args] --rpc-url <RPC>` — read.
- `cast logs --from-block <n> --address <addr> --rpc-url <RPC>` — event logs.
- `cast 4byte <selector>` / `cast 4byte-decode <calldata>` — selector lookup.
- `cast run <txhash> --rpc-url <RPC> -vvvv` — trace (archive node).
- `cast sig "<sig>"`, `cast keccak <data>` — hashing.
