# v4 Hooks — expanded reference

Source: internal audit defaults (post GoldPesa GPXHooks $115K, Base, 2026-10-02).

## Hook permission bit map (lowest 14 bits of the hook address)

| Flag | Bit | Flag | Bit |
|------|-----|------|-----|
| BEFORE_INITIALIZE | 0x2000 | AFTER_INITIALIZE | 0x1000 |
| BEFORE_ADD_LIQUIDITY | 0x0800 | AFTER_ADD_LIQUIDITY | 0x0400 |
| BEFORE_REMOVE_LIQUIDITY | 0x0200 | AFTER_REMOVE_LIQUIDITY | 0x0100 |
| BEFORE_SWAP | 0x0080 | AFTER_SWAP | 0x0040 |
| BEFORE_DONATE | 0x0020 | AFTER_DONATE | 0x0010 |
| BEFORE_SWAP_RETURNS_DELTA | 0x0008 | AFTER_SWAP_RETURNS_DELTA | 0x0004 |
| AFTER_ADD_LIQUIDITY_RETURNS_DELTA | 0x0002 | AFTER_REMOVE_LIQUIDITY_RETURNS_DELTA | 0x0001 |

Read `address & 0x3FFF` and compare to `getHookPermissions()`.

## GoldPesa root cause (the canonical case)

`beforeSwap` burned protocol-owned liquidity inside the *attacker's own open unlock* via
`PositionManager.modifyLiquiditiesWithoutUnlock(BURN_POSITION + TAKE_PAIR)`. The attacker parked an
unsettled mint debt (-114,999.99 USDC) on the PositionManager in that unlock; `TAKE_PAIR` withdrew
only the net (148,868.60 - 114,999.99 = 33,868.60), silently paying the attacker's debt; the attacker
then burned their own position for 114,999.99 USDC out of the PoolManager.

Lesson: a hook called by the PoolManager runs inside the *swapper's* unlock. Shared-delta operations
there can settle someone else's debt. Missing clean-ledger assertion
(`currencyDelta(PositionManager, c0) == 0 && currencyDelta(PositionManager, c1) == 0`) is the root cause.

## Known findings in scope (this program)

| Target | Chain | Address | Severity |
|--------|-------|---------|----------|
| GPXHooks | Base | `0x4519e2b040ff1B64fa03abe2AeF0BC99D7CcEaA8` | CRITICAL (attack tx `0x5c1febd5047c2a15c37988b6abd5c8b984236dddf6fd24eed96b0f43951ad2c9`, block 52078501) |
| Mooney FeeHook | ETH + 2 ARB | `0x1b9f3544dC4915E0C08882d1C3F39B6E464E4844` | dust |
| PubhouseHook | Base | `0x4ab61d774b170d0610fdcc5559aae2c356c600c8` | ~$85 |
| VieTokenPoolHook | Base | `0xa3885fff57cb16cad60a3cac7e49b0273f562840` | $0 |

GPX rescue fork PoC PASS reclaims 114,999.999186 USDC to vault `0x488445D562bACffd8474BEd3E30e5460AE2Fd659`.

## Checklist (verbatim)

1. Ask "whose unlock is this?" at every hook→PoolManager/PositionManager call site.
2. Swap-triggered economic transitions are the red flag — audit like permissionless fund-movers.
3. Shared-credit withdraw must be preceded by a clean-ledger assertion.
4. Check what ARRIVED, not what burned (balance delta before/after, revert on shortfall).
5. Four canonical patterns: reentrancy via callbacks; permission/flag bypass; donation/direct-call
   bypass; custom-accounting drift.
6. Also: missing `onlyPoolManager`; unvalidated `hookData`; held-out/duplicated fee takes; dust
   `clear()`; fixed-assembly calldata offsets on dynamic ABI; brickable keepers.
7. Hunt: live hooks with BEFORE_SWAP/AFTER_SWAP bits that move protocol liquidity/credits.
