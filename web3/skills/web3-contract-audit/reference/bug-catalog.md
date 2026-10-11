# Full-spectrum bug catalog (operational — beyond hooks)

Run EVERY class on every target, not just the shape the code resembles. Each
item names the concrete check, the tool path, and the canonical case. A class is
covered only with cited locations + verdict; otherwise it is an unknown.
Severity follows fork-proved impact, never pattern severity.

## A. Access control
`cast call <t> "owner()(address)"`, `getRoleMember`/`getRoleAdmin` reads, storage
slot scan for admin slots; list every privileged fn and who can reach it
(EOA? contract? which role?). Unprotected `initialize`, `tx.origin`, multisig
rubber-stamping, public setters. Canon: Nomad init ($190M), Oct-2026 Safe
whitelist re-approval (~$6M).

## B. Reentrancy (single / cross-function / read-only)
Map all external calls (incl. ERC777/721/1155 hooks, flash-loan callbacks,
`receive`/`fallback`); verify CEI ordering; check every view fn consumed as a
price by another protocol for mid-callback staleness. Canon: DAO, Rari/Fei,
Curve read-only family.

## C. Oracles & flash-loan composability
Identify the feed, staleness window, decimals; fork-test single-block
manipulation (flash-loan + swap + read in one tx); check TWAP window and
min/max bounds; empty-pool/first-deposit price. Canon: Mango ($117M).

## D. Arithmetic & rounding direction
Rounding must favor the protocol on BOTH sides; decimal scaling (6 vs 18);
division-before-multiply; `unchecked` on user input; ERC-4626 share inflation +
donation attacks. Prove direction with a two-sided fork test. Canon: Bunni
($8.4M), 79thVault-style admin transfer bypassing LP accounting ($14.35M).

## E. MEV & ordering
Missing `minOut`/`deadline`; first-deposit inflation; sandwiched init/oracle;
predictable randomness; JIT games. Test: backrun/front-run the target flow on
fork and measure the extractable spread.

## F. Signatures & auth
Replay across chains/contracts (chainId, verifyingContract, nonces);
`ecrecover` zero-address acceptance; malleability; `permit` DoS; meta-tx replay.
Test: replay a valid signature in a mutated context on fork.

## G. Proxy & upgrade
1967/1822/beacon/diamond resolution via `web3_storage`; uninitialized impl;
layout collisions; `delegatecall` targets; `_disableInitializers`; UUPS auth;
selector clashes. Canon: Parity, Audius.

## H. Token integration
Fee-on-transfer/rebasing/hook-tokens vs accounting assumptions; blocklists;
non-standard returns (`SafeERC20`?); approvals. Test with the actual weird
tokens the protocol accepts, not mocks.

## I. Liquidation & health math
Collateral factors, rounding-allowed under-collateralization, bad-debt handling,
bonus overflow, partial-liq edges, oracle-vs-index mismatch. Fork-test health
boundaries with adversarial prices.

## J. Bridges & messaging
Sender authentication, peer/trusted-remote checks, replay (nonces/ids),
finality/reorg, refund griefing, stuck-queue DoS. Canon: Wormhole, Ronin,
Nomad, HOT/NEAR Intents refund-greater-than-deposit ($3.86M).

## K. DoS & griefing
Unbounded loops, push-to-reverting-receiver, gas assumptions, keeper brickable
by one bad receiver, dust `clear()` omissions.

## L. Assembly & ABI
Fixed offsets on dynamic ABI, `returndatasize`, memory overlap, proxy selector
clashes. Canon: hardcoded-offset router auth bypass (~$42.6K).

## M. Hook/AMM callbacks (supplement, after A–L)
Whose unlock/session runs the callback; swap-triggered economic transitions as
permissionless fund-movers; clean-ledger assertion before shared-credit takes;
check what ARRIVED not what burned; permission-bit vs declared mismatch;
donation/direct-call bypass; accounting drift. Canon: Cork ($12M), GPXHooks
($115K). Full notes: `reference/v4-hooks.md`.

## Disposition
Fork PASS + asserted value movement = finding (map to bounty scale or
disclosure). Anything else = hypothesis. Negative results report coverage,
fork blocks, and remaining unknowns.
