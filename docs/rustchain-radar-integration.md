# XPEX × RustChain Opportunity Radar — live integration proof

This document records a real XPEX integration with the public RustChain bounty ecosystem for review under RustChain bounty #102.

## What is running

The XPEX Command Center includes a credential-free opportunity radar that reads public open issues from:

- https://github.com/Scottcjn/rustchain-bounties
- GitHub public issues API for `Scottcjn/rustchain-bounties`

The runtime is deployed at:

- https://xpex-dify-brain-production.up.railway.app
- Opportunities view: open the Command Center and choose **Oportunidades**

The application exposes:

- `GET /xpex/api/radar/status`
- `POST /xpex/api/radar/scan`
- `GET /xpex/api/opportunities`

## Pipeline

```text
RustChain public bounty issues
        ↓
XPEX Radar scan
        ↓
bounty/reward/payout filtering
        ↓
reward extraction + fit score
        ↓
dedupe by canonical source URL
        ↓
Supabase xpex_opportunities
        ↓
XPEX jobs → delivery → payment tracking
```

The radar can scan manually from the UI and is also configured to scan on service startup.

## Persistence

The integration persists normalized records rather than treating search results as ephemeral UI cards. Current fields include:

- RustChain issue number as `external_id`
- issue title
- canonical GitHub issue URL
- extracted reward text
- open status
- XPEX fit score
- metadata with provider, discovery timestamp, labels, and upstream update time

A unique partial index on the non-empty source URL prevents the same opportunity from being inserted repeatedly.

## Verified runtime result

On 2026-09-22 the deployed radar populated **58 opportunity records** in the XPEX Supabase opportunity table during the live integration run.

Examples discovered by the running machine included:

- #1579 — Elyan Labs mention in an existing README/docs site
- #1524 — Beacon Atlas agent/world bounty
- #102 — New Capability Pitch
- #446 — upload original videos to BoTTube
- #398 — security quest
- #3074 — RustChain LangChain integration
- #16601 — distribution/video package round

The system does not treat discovery as payout. Claims, deliveries, and payments have separate states.

## Real usage

This integration is already driving work rather than only displaying links:

- XPEX generated a real opportunity queue from RustChain.
- The Cenara media system has a RustChain Proof-of-Antiquity video package in production for #16601.
- XPEX used the discovered #1579 opportunity to add a contextual RustChain/BoTTube ecosystem section to an existing Cenara repository.
- Claim submission status and requested RTC payouts are tracked separately from confirmed payments.

## Safety / anti-spam rules

The agent workflow deliberately separates:

1. discovered
2. qualified
3. executing
4. submitted
5. maintainer accepted
6. paid

A discovered issue is never represented as earned RTC. External actions that require a human account or proof are not fabricated.

## Relevant source

The main radar implementation lives in:

- `api/xpex_command_center.py`

Key implementation commits:

- `1e7235d54760316496cd941cf5828b399db6c8fd` — real public-source radar and UI
- `3b2b33f597ad7f1409a11e4a9f4c4814159928a7` — Supabase schema-safe persistence
- `44addf12d0dd951adc7027f8e6be19cdf8d0d88c` — automatic scan on service startup

## AI assistance disclosure

The integration was built and operated with the XPEX/GXEON agent workflow under the repository owner's authorization.
