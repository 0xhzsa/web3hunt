---
name: web3-contract-audit
description: General Web3/EVM contract audit and on-chain analysis harness for any deployed contract on any chain - DeFi, tokens, bridges, governance, proxies, oracles, NFT, and Uniswap v4 hooks. Use to find exploitable logic in live code, confirm exploits on a mainnet fork, trace and size stolen funds, and build rescue PoCs. Covers access control, reentrancy, oracle/price manipulation, arithmetic/precision, flash loans, signatures, proxy/upgrade bugs, token integration, liquidation math, MEV, cross-chain/bridge, DoS, and AMM/hook-specific issues.
---

# Web3 / EVM Contract Audit & On-Chain Analysis

## When to use

Use this skill for **any deployed smart contract on any EVM-compatible chain** — DeFi (AMMs, lending,
perps, vaults, staking), tokens (ERC20/721/1155/4626/4337), bridges/messaging, governance, proxies/upgrades,
oracles, NFT marketplaces, or Uniswap v4 hooks. The goal is to (a) find exploitable logic in **deployed**
code, (b) confirm a suspected exploit on a mainnet **fork**, (c) trace and size funds, or (d) build a rescue
PoC. If an address has bytecode on a chain, this skill applies. Not limited to Solidity — also Vyper/Yul.

## Environment

- **Foundry** on PATH: `forge`, `cast`, `anvil`, `chisel`, `solar`, `foundryup` (`C:\Users\stagh\.foundry\bin`).
  Verify `forge --version` / `cast --version`.
- **Node** available (`node -v`) for JS tooling; **Python** via the daemon's interpreter.
- Prefer `cast` for every read-only interaction; never hand-roll JSON-RPC when `cast` has a verb.
- Prefer the tools `web3_rpc`, `web3_pool_key`, `foundry` (see **Tools**).

## Step 0 — Resolve the target

1. Confirm chain + RPC: `cast chain-id --rpc-url <RPC>`. See `reference/chains-rpcs-explorers.md` for a
   RPC/explorer table. Derive the RPC from the chain the address is deployed on — do not assume Ethereum.
2. Pull runtime bytecode: `cast code <addr> --rpc-url <RPC>`. Empty → EOA/no code, stop.
3. Get **verified source + ABI** from the explorer API (Etherscan v2, Blockscout v2, Sourcify). If the
   explorer is Cloudflare-protected, fetch with the browser, not raw curl.
4. Unverified? Decompile (heimdall / panoramix) or reconstruct from selectors (`cast 4byte <sel>`) +
   storage (`cast storage`, `eth_getStorageAt`) + event logs.
5. Record: address, chain id, deploy tx/block, deployer, labels, current balance (native + tokens), TVL.

## Step 1 — Map the attack surface

- **Proxy?** Resolve EIP-1967 / EIP-1822 / EIP-897 / beacon / diamond (`facetAddress`, `implementation()`).
  Read `cast storage <proxy> 0x3608...bbc` (1967 impl slot) and the admin/beacon slots. Audit the
  **implementation**, not the proxy. Check for uninitialized implementation and storage-collision risk.
- **Access control**: enumerate owner/admin/AccessControl roles/`tx.origin`/multisig/timelock. Which
  functions are `onlyOwner`/`onlyRole`/unguarded? Flag any privileged fn reachable by an EOA or by a
  role that is itself reachable.
- **Entrypoints & value flow**: list external/public fns that move value, mint/burn shares, set prices,
  change state read by pricing/liquidation. Trace where funds come in and go out.
- **External calls**: callbacks (ERC777/721/1155 hooks, flash-loan callbacks, `onFlashLoan`, `uniswapV3*`,
  `receive`/`fallback`, token transfer hooks) — every one is a reentrancy/state-desync candidate.
- **Trust boundaries**: oracles (which feed, staleness, decimals, manipulation resistance), keepers,
  arbitrary `call`/`delegatecall` targets, user-supplied addresses/calldata/hookData.
- **Tokens held**: query balances of the contract and its pools/vaults for every relevant ERC20.

## Step 2 — Vulnerability checklist (run every class, not just the code's shape)

For paid bounty scopes, start with `reference/bounty-intake.md` (scope
discipline first). The operational per-class checks live in
`reference/bug-catalog.md` — run classes A–M on every target. Then run the
chaining pass in `reference/chained-lows.md`: pair every low with the safety
check guarding it (Veria/XRPL pattern — operation and invariant sharing the
same unchecked arithmetic) and prove the chain end to end:

1. **Access control** — missing modifier, role bypass, unprotected `initialize`, public admin setter,
   `tx.origin`, default-initialized roles, ownership renounce/transfer front-run.
2. **Reentrancy** — single/multi-function, cross-function, read-only (view-based), cross-contract; CEI
   violations; ERC777/721/1155 & flash-loan callbacks; no guard where the lock doesn't cover state.
2b. **Read-only reentrancy** — a view fn used as an oracle/price returns stale mid-callback state.
2. **Arithmetic & precision** — rounding **direction** (must favor protocol both ways), decimal/wei scaling
   (token decimals vs 18), division-before-multiply, unchecked blocks, `int`/`uint` casts, share/asset
   conversions (ERC4626 inflation & first-deposit).
3. **Oracle / price manipulation** — spot price vs TWAP, single-block manipulation, stale/failed feed,
   missing min/max bounds, manipulation via flash loan or donation.
4. **Business/invariant logic** — share↔asset accounting, fee-on-transfer & rebasing tokens, index/rate
   drift, reward-debt accounting, rounding in the protocol's disfavor, invariant breaks under extreme states.
5. **Flash loan / atomic composability** — governance (flash-acquired voting power), liquidations,
   LP/reward manipulation, oracle reads within one tx.
6. **Signature / auth** — EIP-712 replay (missing chainId/nonce/nonce-ordering), `ecrecover` returns
   `address(0)`, malleability, `permit` DoS, meta-tx replay across contracts/chains.
7. **Proxy / upgradeable** — uninitialized impl, storage layout collisions, `delegatecall` to
   attacker-controlled target, missing `_disableInitializers`, flawed `initializer` modifier, UUPS
   upgrade-auth, function-selector clashes.
8. **Token integration** — fee-on-transfer/rebasing tokens break accounting, ERC777 hooks, blocklists,
   non-standard return values, missing `SafeERC20`, blacklistable tokens bricking withdrawals.
9. **Liquidation / health math** — wrong collateral factors, bad-debt socialization, rounding allowing
   under-collateralized borrow, oracle-vs-index mismatch, partial-liquidation edges.
10. **MEV / front-run** — missing slippage/deadline, first-deposit inflation, sandwiched init/oracle set,
    predictable randomness (blockhash/timestamp).
11. **Cross-chain / bridge / messaging** — source-chain validation, replay, finality/reorg, message
    authentication, gas/refund griefing, stuck-message DoS, trusted-remote misconfig.
12. **DoS / griefing** — unbounded loops over user-controlled arrays, push-payment to a reverting
    receiver, gas-limit assumptions, revert-on-receive blocking a queue.
13. **Rounding/dust & frozen funds** — dust `clear()`, rounding to zero, precision loss locking funds.
14. **Assembly / ABI** — fixed calldata offsets on dynamic ABI, memory-safety, `returndatasize` checks.
15. **Uniswap v4 hooks / AMM-specific** → see `reference/v4-hooks.md` (whose-unlock, shared deltas,
    permission bits, `modifyLiquiditiesWithoutUnlock` from swap callbacks, clean-ledger assertions).
16. **Keeper/automation** — one bad receiver bricks the keeper; stale cross-chain rate freeze; unsettled
    deltas.

Full write-ups and canonical case notes: `reference/evm-checklist.md`.
Operational per-class checks (beyond hooks — flash loans, MEV, bridges, bounty
mapping): `reference/bug-catalog.md`.
Bounty intake (scope → triage → report): `reference/bounty-intake.md`.
Rescue ops (fork reclaim PoC, disclosure, standing vault): `reference/rescue-ops.md`.

## Step 3 — Confirm on a fork (proof, not suspicion)

1. Trace the real tx: `cast run <txhash> --rpc-url <RPC> -vvvv` (needs an archive node).
2. Fork at the block before: `anvil --fork-url <RPC> --fork-block-number <N-1>`.
3. Write a Foundry PoC that replays the attacker's calls and asserts the balance/delta you claim.
   `forge test --fork-url <RPC> -vvvv`.
4. A finding is only real when the fork PoC **PASSES** and the asserted value moves. Record exact block,
   tx hash, and numbers. On a live/current block, fork the **current** head to prove it's exploitable *now*.

## Step 4 — Trace and size funds

- Follow native + ERC20 movements victim→attacker; compute USD at the incident block and now.
- Use `cast logs`, `web3_rpc` (`eth_getLogs`, `eth_getTransactionReceipt`, `eth_getBalance`), explorer APIs.
- Output: attacker addresses, flow graph, total lost, and the **recoverable** amount still reachable.

## Step 5 — Rescue (only with explicit human approval)

- Build a fork PoC that reclaims funds to a safe address; assert the delta equals the claim.
- Prefer a private mempool (Flashbots) for any live rescue; coordinate disclosure with the protocol.
- **Never sign or broadcast a live transaction without explicit human approval.**

## Deliverable

A short report: target + chain + block, root cause mapped to the checklist item, fork-PoC result (PASS/FAIL +
numbers), attacker/victim addresses, recoverable amount, rescue/disclosure plan. Include `file_path:line`
references for every code claim.

## Tools

- `foundry` — shell hint: forge/cast/anvil/chisel on PATH. Use for compile/test/script and any cast verb.
- `web3_rpc` — raw EVM JSON-RPC read. `eth_chainId`, `eth_blockNumber`, `eth_getCode`, `eth_getStorageAt`,
  `eth_call`, `eth_getLogs`, `eth_getTransactionReceipt`, `eth_getBalance`. Pass `params` as a JSON array.
- `web3_call` — read-only contract call (`cast call`): target + signature + args + rpc_url.
- `web3_storage` — read a raw storage slot (`cast storage`): proxy impl/admin slots, packing, roles.
- `web3_decode` — decode 4-byte selector + args (`cast 4byte-decode`) from unknown calldata.
- `web3_trace` — trace a tx (`cast run`, archive node) to see the full call path.
- `web3_explorer` — GET a block-explorer API URL for verified source/ABI/metadata (Blockscout v2,
  Etherscan v2, Sourcify). See `reference/chains-rpcs-explorers.md`.
- `web3_pool_key` — compute a Uniswap v4 PoolId (currency0/currency1/fee/tickSpacing/hooks).

## References

- `reference/evm-checklist.md` — full per-class vulnerability checklist + canonical cases.
- `reference/v4-hooks.md` — Uniswap v4 hook permission bits, checklist, known cases.
- `reference/chains-rpcs-explorers.md` — RPC endpoints + explorer/API patterns per chain.
- `scripts/v4_hook_probe.ps1` — quick v4 hook triage.
