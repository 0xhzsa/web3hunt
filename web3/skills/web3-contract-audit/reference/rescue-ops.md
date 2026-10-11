# Rescue ops (reclaim + disclose)

## Fork reclaim PoC (required before any live step)

- `anvil --fork-url <archive-RPC> --fork-block-number <N>` at the incident block
  (or current head for live risks); `forge test --fork-url <RPC> -vvvv`.
- The PoC moves funds to a designated safe address; asserted delta must equal
  the claimed recoverable amount. PASS + numbers, or it is not a rescue plan.

## Live execution (explicit human approval required for every item)

- Prefer a private mempool (Flashbots Protect/MEV-Share) for the rescue bundle.
- Coordinate disclosure with the protocol FIRST; never front-run an in-flight
  rescue or grief a negotiation. Draft the disclosure alongside the PoC: root
  cause → catalog item, fork evidence (block/tx/numbers), affected addresses,
  recoverable amount, concrete fix/revocation requested.
- Track attacker wallets and stablecoin/exchange freeze points; report them,
  do not claim custody powers you don't have.
- **Never sign or broadcast a mainnet transaction without explicit human
  approval. Fork state only until then.**

## Standing safe address (whitehat routing)

User-designated recovery vault: `0x488445D562bACffd8474BEd3E30e5460AE2Fd659`.
Route ALL fork-proven recoveries there unless the protocol names another.
