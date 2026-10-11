# EVM Vulnerability Checklist — expanded

Scope: any deployed EVM contract on any chain. Each class lists what to look for and a canonical case.
Pair with `reference/v4-hooks.md` for AMM/hook-specific items.

## 1. Access control
- Missing / wrong modifier on a privileged fn (mint, withdraw, setOracle, upgrade, pause, sweep).
- `initialize()` callable by anyone, or callable twice; missing `_disableInitializers()` on the impl.
- Role that is itself held by a public/derivable address; `DEFAULT_ADMIN_ROLE` left unset.
- `tx.origin` auth; `require(msg.sender == tx.origin)` bypass via malicious contract.
- Ownership transfer/renounce races; `onlyOwner` on a fn that also must be reachable by a contract.
- Cases: Nomad `initialize` ($190M, 2022), Wormhole guardian, Ronin multisig ($624M, 2022).

## 2. Reentrancy (incl. read-only & cross-function)
- State written after an external call (CEI violation); no `nonReentrant` guard on a value path.
- Callback surfaces: ERC777 `tokensToSend`/`tokensReceived`, ERC721 `onERC721Received`,
  ERC1155 `onERC1155Received`, flash-loan `onFlashLoan`/`uniswapV2Call`, `receive`/`fallback`,
  `uniswapV4`/V3 swap callbacks, native transfer to a contract.
- **Read-only reentrancy**: a view used by an external protocol (e.g. `getReserves`, `pricePerShare`)
  read mid-callback returns a manipulable value. Canonical: Curve/Vyper `read-only` reentrancy (2023),
  Balancer `getRate` (2023).
- Cross-function: two fns share state with no shared lock.
- Cases: The DAO ($60M, 2016), Rari/Fei FEI-3 ($80M, 2022), Cream/Curve reentrancy.

## 3. Arithmetic & precision
- Rounding direction: does division round in the **protocol's** favor on both deposit and withdraw?
- Decimal scaling: mixing 6-decimals (USDC/USDT) with 18-decimal math; `10**decimals` assumptions.
- `unchecked { }` blocks around user-influenced values; overflow in `unchecked`.
- Truncation to zero (dust) locking funds; `mulDiv` overflow and sign errors.
- First-deposit / donation share inflation (ERC4626): attacker sends tokens then `donate` to inflate
  `pricePerShare`, victim's deposit mints ~0 shares.
- Cases: Bunny/`mulDiv`, Hundred Finance (empty market rounding), Yearn share inflation family.

## 4. Oracle & price manipulation
- Spot reserves / `slot0`/`slot0.sqrtPriceX96` read directly as a price (manipulable via swap/flash loan).
- TWAP with too-short window; missing staleness/round checks (`latestRoundData` `updatedAt`,
  `answeredInRound`); wrong decimals (`latestAnswer`).
- First-deposit / empty-pool price = 0 or attacker-set.
- `getReserves`/`balanceOf` used as price without manipulation resistance.
- Cases: Mango Markets ($117M, 2022, spot oracle), Value DeFi, Harvest, Cream/Yearn (flash-loan oracle),
  Inverse, Rari Fuse.

## 4b. Flash loan / atomic composability
- Governance: borrow → vote → repay in one tx (make voting power snapshot-based/time-locked).
- Liquidations / rewards manipulable within one tx.
- Any price/state read that can be moved earlier in the same tx.

## 5. Signature / auth
- EIP-712 replay across chains/contracts (missing chainId or verifyingContract); missing/looped nonce.
- `ecrecover` returning `address(0)` accepted as valid signer.
- Signature malleability (high-s, `v` handling); `permit` front-run/DoS; deadline missing/0.
- Meta-tx replay; unchecked signer recovered from `v,r,s` without `<= secp256k1n/2`.

## 6. Proxy / upgradeable
- Uninitialized implementation that can be initialized + `selfdestruct`/upgrade.
- Storage-layout collision between proxy and impl; new vars prepended on upgrade.
- `delegatecall` to a user-controlled target; `upgradeToAndCall` with unvalidated data.
- UUPS missing `_authorizeUpgrade`; transparent-proxy selector clash; beacon owner compromise.
- Cases: Parity multisig ($150M, 2017), Audius ($6M, 2022), Level Finance.

## 7. Token integration
- Fee-on-transfer / rebasing tokens break `balanceOf` accounting (assume amount sent == received).
- ERC777 hooks enabling reentrancy; blocklists/blacklists bricking withdrawals.
- Non-standard ERC20 (returns no bool, returns false); missing `SafeERC20`.
- `approve` race / infinite approves; `transferFrom` not checking return.

## 8. Liquidation / health math
- Wrong collateral factors; rounding allowing under-collateralized borrow.
- Bad-debt socialization error; liquidation bonus overflow; partial-liq edges.
- Oracle-vs-index price mismatch; stale price used for liquidation.

## 9. MEV / ordering
- Missing slippage (`minOut`) / `deadline`; first-deposit share inflation.
- Sandwiched oracle init/update; predictable randomness (`block.timestamp`/`blockhash`/`difficulty`).

## 10. Cross-chain / bridge / messaging
- Source-chain sender not authenticated; missing `peer`/trusted-remote check.
- Message replay (no nonce/id consumed); reorg/finality handling; gas/refund griefing.
- Stuck/blocked message queue (one bad message bricks all); rate-limit/limit math overflow.
- Cases: Wormhole ($326M, 2022, forged guardian), Ronin (validator keys), Nomad (free-for-all),
  Poly Network ($611M, 2021), Multichain, Harmony Horizon ($100M, 2022).

## 11. DoS / griefing
- Unbounded loops over user-growable arrays (gas grief); push-payment to reverting receiver.
- `require(success)` on a transfer to a contract that reverts on receive → queue blocked.
- Gas-limit assumptions breaking on mainnet; storage-bloat DoS.
- Cases: Akutars, Governor-Bravo proposals, various airdrop loops.

## 12. Assembly / ABI
- Fixed calldata/memory offsets on dynamic ABI (arrays, bytes); `returndatasize` not checked;
  `mload`/`mstore` overlap; selector collision in proxies/plugins.

## 13. Uniswap v4 hooks / AMMs
See `reference/v4-hooks.md`. Key: hook called by PoolManager runs in the **swapper's** unlock; shared
`currencyDelta`; `modifyLiquiditiesWithoutUnlock` from a swap callback; permission-bit vs.
`getHookPermissions()` mismatch; missing clean-ledger assertion before a shared-credit `TAKE_PAIR`.

## Universal evidence bar
A finding is real only when: code is verified/decompiled on the **live** chain + a fork PoC **PASSES** on
the **current** block asserting a concrete value move + value at risk is quantifiable. Otherwise it is a
hypothesis, not a finding.
