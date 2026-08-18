# Reference Machine — Apple M1 / 8 GB

This machine is the initial constrained-hardware reference target for LOOM.

## Memory baseline, normal desktop load

Model OFF:
- PhysMem used: 6529 MB
- Wired: 2058 MB
- Compressor: 811 MB
- Unused: 1101 MB
- memory_pressure free: 62%
- Swap used: 1857.19 MB

Model ON — Qwen 3.5 4B MLX:
- PhysMem used: 7500 MB
- Wired: 2037 MB
- Compressor: 3131 MB
- Unused: 130 MB
- memory_pressure free: 32%
- Swap used: 3833.81 MB

The machine was intentionally measured under realistic desktop load rather than after closing normal applications.
