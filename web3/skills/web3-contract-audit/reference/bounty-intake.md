# Bug-bounty intake (Immunefi / Cantina / Code4rena / Hats)

## Take the scope literally

Pull the program page and extract: in-scope contracts (exact addresses + chains
+ versions), out-of-scope contracts and attack classes, severity/payout tiers,
disclosure + KYC rules, and whether the code is a snapshot, upgradeable proxy
set, or live deployment. Work ONLY in-scope targets. Out-of-scope findings are
unknowns with the exclusion cited — never vulnerabilities.

## Triage order (highest expected value first)

1. Privileged roles + upgrade paths: who can move funds or change logic TODAY
   (`owner`, roles, multisig signers/thresholds, timelock delay, `initialize`).
2. External value-moving entrypoints: mint/burn, withdraw/redeem, liquidation,
   claim, bridge send/receive, fee-taking callbacks (`beforeSwap`/`afterSwap`
   with delta returns, router callbacks).
3. Trust boundaries: oracles (feed, staleness, decimals), keepers,
   `hookData`-style passthrough calldata, arbitrary `call`/`delegatecall`,
   user-supplied addresses. Diff the audited snapshot vs what is DEPLOYED —
   patches and "simplifications" are rich ground.
4. New/changed code first; then run the full `reference/bug-catalog.md` pass.

## Report shape (one finding per report)

Title; severity mapped to the program scale; scope proof (in-scope address +
chain); root cause with `file_path:line` refs; fork-PoC evidence
(block/tx/numbers, rerunnable `forge test`); impact in concrete value terms;
fix. Duplicate-check public findings on the same code first. Follow the
platform template; attach the PoC, not screenshots of it.

## Never submit

Unproven patterns, out-of-scope contracts, testnet-only behavior as mainnet
impact, gas notes as security findings, anything produced by breaking program
rules. If the program is invite-only or KYC-gated, say so and stop.
