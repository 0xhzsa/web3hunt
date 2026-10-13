# Fork patterns (proven recipes — copy, adapt, run)

All patterns below are proven working on Base via Tenderly gateway + forge 1.8.3.
Environment facts first: the agent shell is **PowerShell** (`;` chains, no `&&`);
foundry is at `C:\Users\stagh\.foundry\bin` (call `cast`/`forge` by full path or
prepend to `$env:Path` per command); Tenderly caps `eth_getLogs` at 1000 blocks
(chunk every scan) and rate-limits bursts (sleep + retry, never parallelize scans).

## A. Exact replay (ground truth for everything else)

1. From Swap logs take a real recent tx: `eth_getTransactionByHash` → from/to/value/input.
2. Embed the full calldata in a forge test; fork the PARENT block.
3. `vm.prank(SENDER); (bool ok,) = ROUTER.call(DATA); require(ok)` and compare
   emitted-log count against the mainnet receipt. PASS = harness validated.
   Lesson: always validate the harness on a real tx before any variation test.

## B. Origin parity (quoter-divergence / backdoor detector)

Same calldata, same sender, different `tx.origin` — the ONLY variable:
```solidity
uint256 snap = vm.snapshotState();
vm.prank(SENDER);
bytes32[] memory d1 = _run();          // recordLogs + digest each log
vm.revertToState(snap);                // MANDATORY: runs share nothing
vm.prank(SENDER, ALTORIGIN);
bytes32[] memory d2 = _run();
// assertEq lengths + each digest
```
Without the snapshot, run 2 executes on run 1's state and any revert is
meaningless (learned the hard way). Divergence = origin-dependent execution.

## C. Donation parity (direct-call / balance-trust detector)

Baseline run on pristine state; revert; donate dust DIRECTLY to the accounting
contract (`deal` + `transfer`, no `donate()` call); re-run identical swap;
compare full log sets. Material divergence = accounting trusts raw balances.

## D. Direct-PM sender parity (when no router tx exists)

`unlockCallback` skeleton: decode (key, params, to) → `swap` → decode delta
via `signextend` assembly (never `int256(uint256(...))` casts — they revert on
negatives) → settle debts (`settle{value:}` for native, transfer+`settle()` for
ERC20) → `take()` outputs. Compare returned deltas across senders.
Debugging `CurrencyNotSettled`: the hook may take fees mid-swap (trace shows
`take` to treasury/self + `settleFor`); your `take(fullDelta)` then overdraws.
Read the trace, compute the residual, and either cover it or switch to pattern A.

## E. Proving rules

- eth_call `result: "0x"` on state-changing probes means NOTHING (gateways return
  it for message-less reverts too) — see bug-catalog probing discipline.
- `cast call` decodes by the signature YOU supply; a decode error means your
  signature is wrong, not that the contract is broken.
- Tenderly `eth_getCode` can glitch on odd addresses (returned `0xef` for a live
  token); cross-check with a view call before concluding anything.
- `trace_call`/`debug_traceCall` exist but 429 under load; design tests to work
  from logs + return values instead.
- Anvil fork works for execution tests but spawns one process per launch —
  always kill stale `anvil` processes before starting a run.
