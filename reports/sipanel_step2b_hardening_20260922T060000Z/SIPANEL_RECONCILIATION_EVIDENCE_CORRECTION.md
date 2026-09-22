# SIPANEL Reconciliation Evidence Correction (STEP 2B-HARDENING, run 20260922T060000Z)

## 1. The defect

The STEP 2B pilot script recorded reconciliation like this:

```python
out['reconciliation'] = {r.display_name: r.reconciliation_json
                         for r in (base | opt).mapped('current_revision_id')}
```

`sipanel.quote.scope.revision.display_name` is built from the order and the
Scope code, and **both revisions of the pilot order share it**:

```
SI-26/960 / SIPANEL-SEPBILL-PILOT-20260921T021500Z-MASTER r1
```

So the dictionary had one key. The second revision silently overwrote the first
and **only one revision was ever in the evidence**. The STEP 2B reports
nevertheless stated `problems: []` "on both Scopes" — a conclusion the evidence
as written did not support.

The underlying reconciliation was never wrong; the *record* of it was.

## 2. The correction

Evidence is now a **list keyed by the immutable revision id**
(`evidence/reconciliation/pilot_reconciliation_by_revision.json`, generator
`evidence/scripts/reconciliation_evidence.py`). Each entry carries revision id,
quote Scope id, component rows, projected Sale Lines, anchor amount,
separately-billable amount and problems, plus the order, seal hash and resolved
language.

Two explicit flags are computed and stored in the file itself:

```json
"distinct_revision_records_present": true,
"all_problems_empty": true
```

The first is what licenses a "both Scopes" statement: it is true only when both
requested revision ids produced their own distinct record.

## 3. Regenerated result — revision 886 and revision 887 separately

Generated from the **retained** STEP 2B pilot records (order `SI-26/960`
cancelled, Scopes 818/819 archived, revisions and generated lines retained).

### Revision 886 — base Scope 818 (not optional)

| | |
|---|---|
| Revision state | `accepted_sealed` |
| Quote Scope | 818, acceptance `base` |
| Resolved language | `fa_IR` |
| Anchor amount | **30,000,000** |
| Separately-billable amount | **12,300,000** |
| Projected lines | 2 |
| **Problems** | **`[]`** |

| Line | Origin key | Component | Qty | Subtotal | Invoice gate |
|---:|---|---:|---:|---:|---|
| 1770 | `886:d2f9a9fe…` | 6118 | 24 | 10,800,000 | — |
| 1771 |  `886:2a8f4ea9…` | 6119 | 1 | 1,500,000 | **provisional** |

### Revision 887 — optional Scope 819 (accepted)

| | |
|---|---|
| Revision state | `accepted_sealed` |
| Quote Scope | 819, acceptance `accepted` |
| Resolved language | `fa_IR` |
| Anchor amount | **0** |
| Separately-billable amount | **6,000,000** |
| Projected lines | 2 |
| **Problems** | **`[]`** |

| Line | Origin key | Component | Qty | Subtotal | Invoice gate |
|---:|---|---:|---:|---:|---|
| 1772 | `887:f3c2ce29…` | 6123 | 10 | 4,500,000 | — |
| 1773 | `887:ddc60cc4…` | 6124 | 1 | 1,500,000 | — |

### Cross-check against the order

```
anchor 886      30,000,000
separate 886    12,300,000
anchor 887               0
separate 887     6,000,000
                ──────────
                48,300,000   = the pilot order's untaxed total at confirmation ✓
```

The two revisions carry **different** anchor and separate amounts, which is the
clearest demonstration that the earlier single-entry evidence could not have
described both.

## 4. Statements corrected

Both affected sentences in the STEP 2B report directory now carry an inline
correction note naming the collision and giving the per-revision figures:

| File | Original claim |
|---|---|
| `SIPANEL_COMMERCIAL_RECONCILIATION_REPORT.md` | "Per-revision reconciliation for both Scopes is in `evidence/pilot/pilot_result.json` under `reconciliation`, with `problems: []`." |
| `SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_REPORT.md` | "**48,300,000** ✓, with `problems: []` on both Scopes." |

**The STEP 2B ZIP was deliberately not rewritten**, on the same principle applied
to the STEP 2A bundle: a delivered bundle is a frozen record of what was
delivered. Editing the two markdown files therefore makes them diverge from the
STEP 2B `SHA256SUMS`, which is expected and recorded here:

| File | Hash in STEP 2B SHA256SUMS | Hash after correction |
|---|---|---|
| `SIPANEL_COMMERCIAL_RECONCILIATION_REPORT.md` | `4f2c0f23…` | `4c361b76…` |
| `SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_REPORT.md` | `8cec7489…` | `120170b6…` |

`SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_BUNDLE.zip` still verifies against
its own `.sha256`. Every other file in that directory still matches.

## 5. The pilot script itself

`reports/sipanel_separately_billable_.../evidence/scripts/pilot_2b.py` retains
the collided line, because it is the historical record of what was executed. The
corrected generator is a separate script in this run's directory, and any future
pilot should key evidence by immutable id, never by a display name.
