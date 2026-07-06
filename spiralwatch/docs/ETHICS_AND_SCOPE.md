# Scope

SpiralWatch, as built in this repo, is an **analysis and simulation** system. It is not
authorized to take action against real accounts or real content on any platform.

## What this means concretely

- `scrapers/` may only call public read APIs (e.g. the AT Protocol public endpoints) to
  collect posts, authors, and reply relationships. No posting, following, reporting,
  or account-level write actions of any kind.
- `analytics/` produces scores (ARI, EAS, WCS, feeder-node composite, etc.) as research
  output. A score is a hypothesis about a real, identifiable person's public behavior —
  treat outputs as provisional and avoid publishing per-account rankings outside the
  research context that produced them.
- `response_simulation/` (the former "intervention" layer) runs exclusively against the
  synthetic diffusion engine in `core_math/`. Every module sets
  `requires_authorization = True`. Nothing in this package is wired to any live platform
  API, and it should stay that way unless a separate, explicit authorization decision is
  made — see `triage/authorization.py`.
- `triage/authorization.py` is a hard gate, not an advisory one: it exists so that if
  someone later tries to connect `response_simulation` to a real platform, there is one
  place that has to explicitly allow it, and one audit log (`triage/audit_log.py`) that
  records the decision.

## Why

A "radicalization index" computed about a real person is a claim about them, not a fact.
False positives, chilling effects on legitimate (if unpopular) speech, and harassment
risk if rankings leak are all real failure modes of this kind of system. Keeping
analysis and action strictly separated is what makes the research usable without those
costs.
