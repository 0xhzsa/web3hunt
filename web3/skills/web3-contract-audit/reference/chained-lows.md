# Chained lows → criticals (Veria/XRPL pattern, Sep 2026)

Canonical: two bugs, harmless alone, $94B together. `BookStep` aggregated 256
offers with unchecked int64 `operator+=` (charge wrapped to 256 drops while
makers got trillions); the `XRPNotCreated` invariant used the SAME unchecked
int64 math and wrapped identically into a false negative. 18.45T units in one
ordinary tx, repeatable, no special access. Fixed in `rippled v3.4.1` (checked
summation + widened accumulator). $250K max bounty. General agents pointed at
the code afterwards still could not find it.

## The hunt (run after the single-bug pass, every target)

1. List every low/informational: unchecked arithmetic sites (`unchecked {}`,
   casting, int128/int256 mixes, share math), loose invariants/caps/assertions,
   odd-but-tolerated sums.
2. Pair them: does any SAFETY CHECK compute with the same types and same missing
   checks as the operation it guards? Priority pairs:
   - aggregation loops + post-tx invariants / supply conservation
   - share-price math + deposit/withdrawal guards
   - fee accounting + fee-burn assertions
   - voting snapshots + quorum checks
   - bridge amount tracking + mint caps
   - hook/AMM custom accounting + settlement assertions
3. The tell: both halves share one root-cause shape (same int type, same
   unchecked operator, same missing bound). Demand BOTH halves hardened.
4. Prove end to end on fork/local net: setup + trigger + the check's false
   negative + spendability of proceeds. Unproven chain = two unrelated lows.

## EVM tool paths

- Find unchecked sites: `cast disassemble` / decompiler scan for `unchecked`
  blocks; trace `mulDiv`/casting in share math via `web3_trace` on real txs.
- Test wrap behavior on fork: `forge test` with boundary values (2^56-scale
  inputs, 256-entry aggregations, cap-adjacent balances); assert the invariant's
  verdict alongside the operation result — the divergence IS the finding.
- Same pass applies to non-EVM lanes (L1 clients, relayers, firmware): reuse
  the method, change the toolchain.

## Disposition

Chained criticals outrank single-bug findings of equal face severity. Report
both halves, the combined PoC, and the two-part fix. Audited/bounty-hardened
codebases are explicitly in scope — decade-old reviewed code hid this class.
