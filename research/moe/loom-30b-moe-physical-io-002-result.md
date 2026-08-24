# LOOM 30B MoE Physical I/O 002 — Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`
Run: `20260824T062607Z`

## Device verification

Physical backing device: `disk0` — internal APPLE SSD AP0256Q. Model volume path resolved `/dev/disk3s5 -> disk3 -> disk0s2 -> disk0`.

Device evidence used `iostat -Id -c 2 -w 1 disk0`. Idle/background windows were measured and conservatively bounded/subtracted.

Warm control requested 1,075,396,608 B while only ~71.21 MB was observed at the device (~67.41 MB conservative net), confirming that warm process throughput can be served substantially from memory/cache.

Cache-minimized gate requested 12,533,760,000 B and observed 11,526.89 MB raw / 10,972.89 MB conservative net device transfer. Conservative device-byte coverage was 87.55%, so the physical-device gate passed.

## Canonical physical results

- Sequential device-verified throughput: 2,391.9 MB/s.
- Random expert-sized application throughput: 1,993.6 MB/s.
- Random expert-sized physical throughput: 1,890.4 MB/s.
- One expert read size: 2,506,752 B.
- Expert latency: P50 1.197 ms; P90 1.509 ms; P95 1.643 ms; P99 2.019 ms.
- Top-k=8 physical throughput: 1,823.1 MB/s.
- Top-k=8 latency: P50 9.839 ms; P90 12.622 ms; P95 13.159 ms; P99 14.783 ms.
- Token-like 384-read latency: P50 460.074 ms; P90 461.431 ms; P95 461.611 ms.
- Token-like physical throughput: 1,998.8 MB/s.
- Device coverage: sequential 101.49%; random 94.82%; top-k 94.73%; token-like 95.40%.

## Zero-cache storage economics

Zero-cache routed-expert traffic is 962,592,768 B/token (918 MiB/token).

Device-verified I/O-only lower bound:
- 0.4816 s/token;
- maximum 2.076 tok/s from storage alone.

Required external-traffic reduction from this storage-only baseline:
- 1 tok/s: 0%;
- 2 tok/s: 0%;
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

These are necessary I/O-only reductions, not sufficient end-to-end targets. Real runtime compute, tensor creation, routing, dequantization, KV and sampling add latency, so practical 5/10 tok/s operation would require at least these reductions and likely more.

## Expert-pack implication

Expert-major packing keeps bytes/expert unchanged at 2,506,752 B but reduces source range reads from 9 to 1. At the measured physical rate, transfer time is about 1.25 ms/expert. The exact wall-time benefit of 9 -> 1 syscall/range dispatch remains unisolated, so a full 14.344 GiB repack is still conditional rather than automatically promoted.

## Decision

Physical storage is now proven and is not structurally prohibitive for external-expert research. However zero-cache execution is capped near 2 tok/s before compute, so cache/reuse and/or multi-token block amortization are primary requirements for materially higher performance.

One-layer external-expert execution remains scientifically justified as the next runtime proof, and DFlash/block-routing overlap remains a high-value parallel branch because the required 58–79% traffic reduction for 5–10 tok/s must come from avoiding repeated expert movement rather than raw SSD speed alone.

Raw local evidence: `results-local/moe/physical-io-002/20260824T062607Z/`.
