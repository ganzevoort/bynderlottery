# general
- monitoring; metrics: #accounts, #unverified, #ballots, #winners etc

# backend
## accounts
- captchas
- 2fa
- remove old unverified accounts?
- test views, management commands only when LAYER=test
- emails refer to /oldstyle/ urls

## lottery
- payout for winners
- payment for ballot purchases
- remove ballots without prize for closed draws older than X.

# cicd pipeline
- push to gitlab
- setup pipeline to do tests
- and to deploy to production (k8s)
