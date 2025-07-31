# general

- monitoring; metrics: #accounts, #unverified, #ballots, #winners etc
- pip audit, yarn audit

# backend

- reduce container size by:
  - use alpine (26M)
  - install ipdb only in dev (35M)
  - don't include postgresql-client (?)

## accounts

- captchas
- 2fa
- remove old unverified accounts?

## lottery

- payout for winners
- payment for ballot purchases
- remove ballots without prize for closed draws older than X.
