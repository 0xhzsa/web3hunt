# International alpha (CN/KR-led incident intel → transferable technique)

Post-mortems are excluded as TARGETS (never-exploited rule) but mined for
TECHNIQUE. Each entry: what happened, the transferable shape, where to hunt it
now. Sources monitored: DeFiHackLabs PoCs (SunWeb3Sec, 889 incidents,
fastest public reproductions), SlowMist hacked DB + reports, ChainCatcher /
Odaily / Foresight / PANews (CN fast technical coverage), TokenPost + MK (KR
originated cases), Xangle research.

## 1. KelpDAO rsETH $292M — off-chain quorum failure (KR sources, Apr 2026)

Not a contract bug: Lazarus DDoS'd third-party RPCs, compromised 2
LayerZero-hosted internal RPC nodes, fed a single-DVN verifier forged Unichain
burn data; Ethereum side released 116,500 rsETH. Nodes self-destructed
(binaries + logs wiped). A second 40k-rsETH ghost packet was stopped by pause +
SEAL-911 blacklist; Arbitrum froze ~30,766 ETH.
Transferable checks for EVERY bridge/intent integration hunted:
- Verifier quorum: single-DVN config = critical by itself. Demand N-of-M with
  independent operators; prove the config on-chain, not in docs.
- Off-chain infra threat model: RPC diversity, compromise detection, binary
  attestation for hosted nodes.
- Cross-chain invariant monitor (Chainalysis lesson): source-burn vs
  dest-mint mathematical match in real time — first unmatched release halts.
- Ghost-packet pattern: replayed/forged second payouts after the first; watch
  for duplicate message IDs and pause wiring that actually pauses.

## 2. Set Protocol `actualizeFee()` rounding bump, flash-amplified (Oct 2026)

Fee-accrual rounding pushed upward per call, amplified into collateral drain
via Uniswap v4 flash execution. Hunt shape: fee-accrual functions with
round-up + an executor path (flash/callback) that repeats them at scale.
Pair with the guard: does any cap/rate-check see the AGGREGATE, or per-call?

## 3. Perp v2 (Curie) unguarded funding-growth update → vault drain (Oct 2026)

Anyone could push funding-growth state; vault paid out on the manipulated
value (~3,062 USDC). Hunt shape: global market-state setters (funding,
index, rate accumulators) reachable without privilege + downstream payout
that trusts the latest value without TWAP/bounds.

## 4. MOKE `settle()` tx.origin check + price manipulation (Oct 2026, BSC)

`tx.origin` auth plus a manipulable price → ~41.68M over-mint. Hunt shape:
`tx.origin` anywhere near mint/settle/redeem, COMBINED with any price input
(spot, single-block TWAP, caller-supplied). Either half alone reads low.

## 5. Pancake V3 swap-helper signed-delta bug (Oct 2026, BNB)

Sign handling in swap-helper deltas drained ~1.65 BNB. Hunt shape: every
int128/int256 delta path — specified vs unspecified, exact-in vs exact-out,
fee-on-transfer tokens shifting signs. Fuzz both directions with extreme
values; assert conservation, not just no-revert.

## 6. FlashLoopAdapter broken self-attestation (~114 ETH, Oct 2026)

Adapter asserts its own safety properties; the attestation itself was the
hole. Hunt shape: adapters/relayers/keepers whose `verify`/`check` reads
caller-influenced state, and any `onlyAdapter`-style trust that bottoms out
in an unvalidated registration call.

## 7. SKYDAO burn-from-pair + premature sync (Oct 2026, BSC)

Burn LP from the pair then sync reserves early (~59.9K USDT). Hunt shape:
reserve-sync ordering vs burn/skim entrypoints; `sync()` callable ahead of
accounting updates; skim-then-sync sequences.

## 8. MakerDAO flip-keeper unprotected drain selector (Oct 2026, 200 ETH)

Unauthenticated keeper function granted Vat delegation to an attacker module,
settling 2020 zero-bid lots. Hunt shape: legacy/keeper/auxiliary contracts
holding OLD permissions (hope/delegate/approve) with unguarded setters —
audit the dusty corners, not just the core. (Already exploited: pattern only.)

## Lanes and honesty notes

- CN lane is the strongest non-EN source (DeFiHackLabs PoCs, SlowMist DB,
  fast trade press). KR lane is strong for Korea-originated cases (TokenPost,
  Xangle, MK/Chainalysis writeups). JP/RU lanes were thin this pass — recorded,
  not padded.
- Every pattern above enters hunts as a CHECK, never as a target. A live
  target matching one still needs the full evidence bar (live code, value NOW,
  permissionless path, fork PoC).
