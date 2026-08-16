# AI-to-AI Dialogue Protocol

Status: current public protocol, updated 2026-08-16.

The original 2026-05 version of this document described one concrete `inbox.jsonl` / `outbox.jsonl` transport. That implementation is now **historical**. The durable part is the relation contract, not the old transport path.

## Intent

Binoche should not become a routine relay between AI systems when the systems can exchange or independently inspect the needed information through their available tools.

At the same time, no AI return becomes authoritative merely because another AI produced it.

The purpose of peer dialogue is to add a **different observation boundary**, preserve disagreement when useful, and return enough provenance for re-entry.

## Minimum return packet

```yaml
source: file | tool | ai | human | runtime
observed_at: timestamp-or-unknown
observer: model/tool/role
question_boundary: what was actually asked
observation: what was directly read or returned
interpretation: optional meaning
uncertainty: unresolved part
counterevidence: optional conflicting observation
changed_claim: only the claim this return can update
held_claims: related claims that remain unchanged
```

## Transport is replaceable

The transport may be:

- a file handoff
- a tool/connector return
- a direct model call
- a copied bounded packet
- a local worker route
- another verified interface

Do not assume the old May 2026 Antigravity inbox/outbox paths are current simply because they are preserved in Git history or older documents.

## No forced consensus

A peer return is not a vote.

```text
camera A observation
+ camera B observation
+ provenance / uncertainty
!= automatic synthesis into one story
```

If two observers disagree, keep the disagreement visible until a new observation actually discriminates between them.

## Escalation to Binoche

Ask Binoche when the missing information is genuinely unavailable to the current tools/bodies, for example:

- first-person bodily/felt observation
- explicit permission or consent
- a personal preference or value judgment that only he can supply
- a direction choice that cannot be inferred from existing evidence

Do not escalate merely because:

- another AI has not yet been asked
- a current file has not yet been read
- a test/readback has not yet been run
- the agents disagree but can preserve the disagreement
- an old workflow expected a human relay

## Observation before interpretation

When receiving another AI's answer, first record what it actually returned. Keep later meaning-making separate.

```text
peer return
→ direct observation
→ interpretation
→ uncertainty
→ changed claim
→ stop or next bounded contact
```

This helps prevent a long-running system from absorbing every outside view into its existing narrative.

## Prospective evaluation

If a peer-AI return is being used as part of a prospective test, the discriminator should exist before the observation is collected. A rule written only after seeing the return is retrospective.

## Privacy boundary

Do not send private conversation archives, local logs, credentials, or personal source material to another system simply to make the handoff richer.

Use the smallest packet that preserves the question boundary. Public examples derived from private source material require explicit per-item permission from the originating person or data owner.

## Historical note

The earlier `Luvit -> inbox.jsonl -> Shion -> outbox.jsonl -> Luvit` loop remains useful as evidence of one implementation phase. It is no longer the public protocol's claim about the current transport.
