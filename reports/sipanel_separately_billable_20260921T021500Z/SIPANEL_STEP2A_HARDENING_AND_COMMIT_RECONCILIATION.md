# SIPANEL STEP 2A Hardening and Commit Reconciliation (STEP 2B, run 20260921T021500Z)

Closes the three STEP 2A prerequisites: P1 accessor hardening, P2 commit
reconciliation, P3 seal-drift enforcement.

---

## P1 — the translation accessor now fails closed

### What was wrong

`sipanel_tools.stored_translations()` carried a compatibility fallback for a
future Odoo that might drop `Text._get_stored_translations`. That fallback read
the field under each installed language and treated a non-empty value as a
stored term:

```python
    if getter is None:                       # REMOVED
        for code, _name in record.env['res.lang'].get_installed():
            value = record.with_context(lang=code)[field_name]
            if value:
                raw[code] = value
```

That is exactly the misclassification STEP 2A was built to prevent. A language
read returns the `en_US` fallback, so **every** installed language would have
looked translated, `has_translation()` would have returned True everywhere, the
`missing` list would always have been empty, and a Persian customer could have
been sent English text with no warning and no block at seal.

### What it does now

```python
    getter = getattr(field, '_get_stored_translations', None)
    if getter is None:
        raise MissingTranslationAccessor(...)
```

`MissingTranslationAccessor` is a `RuntimeError` subclass, deliberately not a
`UserError`: it means the code must be ported to a new ORM accessor, and no
business decision may be taken while it is raised. The message names the model,
the field and the function to port.

| Requirement | Status |
|---|---|
| use the verified Odoo 19 raw accessor | unchanged — `Text._get_stored_translations` |
| fail closed with an explicit technical error if it is absent | `MissingTranslationAccessor` |
| never infer a stored translation from a language-context read | the fallback loop is deleted |
| test simulating accessor unavailability | `test_accessor_unavailability_fails_closed` |
| no behavioural change on the installed Odoo 19 | confirmed — see below |

The test patches the accessor off **the field class** (Field objects may use
`__slots__`, so patching the instance is not reliable), asserts both
`stored_translations()` and `has_translation()` raise, restores it, and then
asserts the normal result is unchanged. `sipanel_commercial_scope_core` went
from 51 to 52 tests with no other change, and every pre-existing translation
test still passes, which is the evidence that installed behaviour did not move.

---

## P2 — commit reconciliation

### Recorded facts

```
$ git rev-parse HEAD
c737034b2f1cf7f30c910eb583bdc852a0c34388

$ git log --oneline --decorate -10
c737034 (HEAD -> master) SIPANEL STEP 2A 20260921T013000Z: native Odoo translation fields …
8d10567 SIPANEL STEP 1D 20260920T105500Z: correct the test-baseline statement and rebuild the bundle
7ae671d SIPANEL STEP 1D 20260920T105500Z: multi-page pagination defect L-02 reproduced and fixed
6820983 SIPANEL STEP 1C 20260920T084541Z: Persian PDF cover overlap reproduced and fixed …
484b884 SIPANEL STEP 1B 20260920T080013Z: D-01 report.url applied …
ca9c474 SIPANEL customer-output validation 20260920T060817Z: reports, redacted evidence …
0e2d63e SIPANEL customer-output validation 20260920T060817Z: D-02 unit names …
46f4135 SIPANEL run 20260919T164530Z: regenerated manifests, SHA256SUMS and bundle …
07d8781 SIPANEL run 20260919T164530Z: documentation-only reconciliation …
cbc246f SIPANEL run 20260919T164530Z: release manifest, bundle manifest, SHA256SUMS …
```

### Which commit contains what

`git show --stat c737034` lists **both** `addons/…` and
`reports/sipanel_native_translation_20260921T013000Z/…`.

| Content | Commit |
|---|---|
| STEP 2A source change (models, migration, views, tests) | **`c737034`** |
| STEP 2A reports, evidence and bundle | **`c737034`** — the same single commit |

### Why the bundle manifest says `8d10567`

`build_bundle_2a.sh` computes `REPO_COMMIT=$(git rev-parse HEAD)` while building
the manifest, and the bundle is built **before** the commit that contains it —
it has to be, because the manifest and the ZIP are themselves committed. So at
build time HEAD was still the previous commit, STEP 1D's `8d10567`.

| Identifier | Verdict |
|---|---|
| `c737034` (reported in the STEP 2A final response) | **correct** — the commit that contains the STEP 2A source and reports |
| `8d10567…` (recorded in the STEP 2A bundle manifest as "Repo commit") | **stale, not incorrect** — it is the parent commit, i.e. HEAD at bundle-build time |

Neither identifier was fabricated and no content is missing. The same one-commit
lag exists in the STEP 1D manifest (`7ae671d` recorded, final state `8d10567`),
from the same build-then-commit ordering.

### Correction applied

The old bundle is **not** rewritten, as instructed. The STEP 2B manifest now
labels the field honestly and records both identifiers:

```
Parent commit at bundle build:  <sha>   (HEAD before this run's commit)
Commit containing this report:  created immediately after the bundle; see
                                SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_REPORT.md
```

and the STEP 2B final response reports the post-commit hash.

---

## P3 — seal-drift enforcement

### What already existed

Two of the three gates were already implemented and are now proven by test
rather than assumed:

| Gate | Where | Behaviour |
|---|---|---|
| customer acceptance refused on drift | `quote_scope_revision.action_accept` | raises; state stays `sent_sealed` |
| confirmation refused on drift | `sale_order.action_confirm` → `_sipanel_accept_current_revisions` → `action_accept` | raises |

### What was missing and is now implemented

| Gate | Where | Behaviour |
|---|---|---|
| invoice creation refused when governed content differs from the accepted seal | `sale_order._sipanel_check_seal_integrity_for_invoice`, called from `_create_invoices` | raises, naming each drifted Scope |

### Tests

| Requirement | Test |
|---|---|
| acceptance refused on drift | `test_seal_drift_blocks_acceptance` |
| confirmation refused on drift | `test_seal_drift_blocks_confirmation` |
| invoice creation refused on drift | `test_seal_drift_blocks_invoice_creation` |
| a commercial change after sealing needs a new working revision and a new seal | `test_commercial_change_after_sealing_requires_a_new_revision_and_reseal` |
| prior artifacts and hashes retained | `test_prior_artifacts_are_retained_after_amendment` |
| a sealed generated line cannot be edited | `test_sealed_generated_line_cannot_be_edited_directly` |

### The retained cancelled order SI-26/312

Its two sealed revisions still do not recompute to their stored hashes, and
**nothing was done about that** — no hash was rewritten and no consistency was
fabricated. The cause is unchanged from the STEP 2A report: the seal payload
includes the live `order.amount_untaxed` / `amount_total`, and that order was
cancelled and edited during the 2026-09-20 validation runs.

It cannot become a usable operational record:

| Property | Value |
|---|---|
| order state | `cancel` |
| acceptance | blocked — `action_accept` requires `sent_sealed` and a matching hash |
| confirmation | blocked — a cancelled order cannot be confirmed, and acceptance would refuse anyway |
| invoicing | blocked — the new `_create_invoices` gate refuses drifted governed content |

It therefore remains exactly what it is: historical drift evidence.

### A legitimate drift that is not a defect

Accepting an optional Scope changes the order total, and the order total is part
of every Scope's seal payload, so **every** sealed Scope on that order drifts.
This is pre-existing and the governed flow already handles it by re-sealing
before confirmation — `test_pt21` in `test_governance.py` documents it in the
existing code:

```python
# accepting keeps the hash consistent (qty is part of the projection, so re-seal happens on next send)
self.assertNotEqual(rev._current_seal_hash(), rev.sealed_hash)
order.action_quotation_send()     # re-seal
order.action_confirm()
```

The live pilot follows that flow (seal → accept → **re-seal** → confirm) and
records the drift explicitly in `evidence/pilot/pilot_result.json` under
`drift_after_acceptance`.
