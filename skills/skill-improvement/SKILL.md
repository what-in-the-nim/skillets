---
name: skill-improvement
description: Record and improve a skill through observed runs.
disable-model-invocation: true
---

# Skill Improvement

Use observed runs to make one evidence-backed improvement at a time. Keep a ledger so the next run can show whether the friction changed.

## Locate

- Find the canonical `SKILL.md`, any installed copy, repository guidance, and existing run ledger. Check the working tree before editing.
- Identify the revision each run actually loaded. A later skill edit cannot explain an earlier run.
- Keep the ledger in the canonical source repository at `docs/skill-improvement/<skill-name>.md`. If there is no source repository, put it beside the canonical `SKILL.md`.

## Record a run

- Read the supplied task or transcript, including relevant tool failures, retries, final output, and publication readback. Inspect each subagent's own trace when delegation affects quality or cost. Use local session logs only for details the task view omits.
- Add one ledger entry with the task link, date, skill revision, lead and worker models/efforts when known, task size, intended flow, observed flow, outcome, and evidence links. Mark missing facts as unknown.
- List friction as a concrete event with its cause if verified, consequence, and evidence. Separate skill behavior from repository, service, credential, and sandbox behavior.
- Record usage and calculate task cost using the rules below. Complete the entry when the lead and every subagent are accounted for, including agents with unavailable usage or pricing.

### Usage and cost

- Define the measured task's start/end and included turns. Keep the improvement analysis itself separate from the run being measured. Include retries, failed work, and nested subagents within that scope.
- Add one row per agent and model/pricing segment: agent ID, parent ID, role, actual model ID, reasoning effort, input tokens, cached input tokens, output tokens, total tokens, elapsed time, tool calls, usage source, coverage, and estimated cost. Record model changes as separate segments. Use `unknown` for missing values and `0` only for confirmed zero usage.
- Read recorded usage from each agent's own trace or provider usage metadata. Sum disjoint per-call increments, or derive deltas from cumulative counters within the same counter scope. Count each usage event once; reconcile parent aggregates with child traces before adding them. Confirm whether cached tokens are included in input and reasoning tokens in output; count each category once. Keep reported totals and flag discrepancies.
- Look up the provider's official rates for the actual model, service tier, and pricing mode, using rates effective at the run date when available. Record the source URL, lookup date, effective date, currency, and input/cached-input/output rates per million tokens. Label current-rate substitutions explicitly. Keep unknown model aliases or unavailable rates unpriced; use a separately labeled proxy only when requested.
- When input includes cached input, calculate `uncached_input = input - cached_input` and `estimated_cost = (uncached_input * input_rate + cached_input * cached_rate + output * output_rate) / 1_000_000`. When input excludes cached input, use it directly as uncached input. Check that counts are nonnegative and cached input does not exceed inclusive input. Apply documented provider rules for separately billed categories; a missing cached count or rate makes the estimate incomplete unless caching is confirmed absent.
- Sum segment costs per agent, then show lead subtotal, all-subagent subtotal, and combined task estimate. Keep full precision until display rounding. Report token totals and usage/pricing coverage alongside cost; label a partial sum as a **known subtotal**, with missing agents or categories listed. Combine only costs in the same currency, or document the conversion rate and date.
- Present this as an **API-equivalent estimate**, unless actual billed charges are available. Subscription usage, quota percentages, and elapsed time do not establish billed cost. Include separately billed tools/services when evidenced, or state that the estimate covers model tokens only.

Use this summary in every run entry and final report:

| Agent / parent / role | Model / effort | Input | Cached input | Output | Total | Estimated cost | Evidence / coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Lead and each subagent; separate rows for model changes | Actual ID or unknown | | | | | | |

Follow the table with the measured scope, pricing sources/rates/currency, lead subtotal, subagent subtotal, combined estimate or known subtotal, and missing coverage. Retain elapsed time and tool-call counts in the ledger when available.

## Compare

- Match each prior friction by the behavior it represents, across changed PRs or tasks. Use `🆕 NEW`, `🔁 STILL_OPEN`, and `✅ FIXED` only when the new run supports that status. Use `⏳ UNVERIFIED` for a changed skill that has not been tried again.
- Check task quality as well as speed: coverage, evidence for findings, outcome, and readback. Note task size and model differences before attributing a token or timing change to the skill.
- Report the observed improvements and remaining friction before proposing another change.

## Improve

- Choose the smallest change that addresses an observed cause. Prefer a clearer step or completion criterion for agent decisions and a deterministic helper for repeated mechanical work.
- When editing a skill, apply the installed `writing-for-agents` skill and its `SKILL-MECHANICS.md`. Preserve the skill's invocation choice unless the observed problem concerns invocation. Apply coding guidance when changing scripts.
- Make the requested edit in the canonical source, update the installed copy when it is used for the next run, and run focused checks. Keep unrelated work intact.
- Record the change and its expected observable effect in the ledger as `⏳ UNVERIFIED`. Mark it `✅ FIXED` only after a later run demonstrates the behavior.

## Deliver

- Give the ledger and changed file links, the before/after observation, checks run, the usage/cost summary above, and the exact signal to look for in the next use.
- If the request is analysis only, record the run and give recommendations. If the user asks to update the skill, implement and verify the change. Commit and push when requested.
