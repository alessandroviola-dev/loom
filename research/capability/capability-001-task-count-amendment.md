# CAPABILITY 001 — frozen task-count amendment

Date: 2026-08-21
Status: FROZEN BEFORE ANY MODEL TASK

## Purpose

Correct a clerical inconsistency in `capability-001-frozen-spec.md` before any CAPABILITY 001 model task is executed.

The frozen specification repeatedly declares a 12-task suite, but the authoritative task identities actually defined are:

- C01, C02, C03, C04, C05, C06 — six coding tasks;
- G01, G02, G03 — three Git-safety tasks;
- E01, E02 — two experimental-reasoning tasks.

This is **11 tasks total**, not 12.

A pre-run audit on 2026-08-21 inspected the frozen specification, context amendment, runtime admission document, and Coding Benchmark 01 v1 assets. It found no additional twelfth task. No model task was executed before this mismatch was detected.

## Authoritative correction

For the canonical CAPABILITY 001 baseline:

- frozen task count = **11**;
- task identities = **C01–C06, G01–G03, E01–E02**;
- primary metric = `primary_passes / 11`;
- percentage denominator = 11.

No task prompt, fixture, expected output, scoring rule, model/runtime setting, tool surface, resource gate, or isolation rule is changed by this amendment.

## Provenance rule

Do not invent a twelfth task to preserve the erroneous nominal count.

The original `capability-001-frozen-spec.md` remains preserved as the pre-amendment frozen document. This amendment overrides **only** references to the suite count/denominator of 12.

All other frozen requirements remain authoritative.

## Scientific status

This correction occurs before CAPABILITY 001 science:

- model tasks executed before correction: **0**;
- model outcomes consumed: **0**;
- retries/rescues consumed: **0**.

Therefore the corrected 11-task suite remains a clean preregistered baseline.