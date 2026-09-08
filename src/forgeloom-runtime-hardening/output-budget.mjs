export function allocateOutputBudget({
  guardInputTokens,
  safeInputTokens = 2800,
  safeTotalTokens = 3600,
  minOutputTokens = 800,
  maxOutputTokens = 1600,
  requestedOutputTokens = maxOutputTokens,
} = {}) {
  const values = {
    guardInputTokens,
    safeInputTokens,
    safeTotalTokens,
    minOutputTokens,
    maxOutputTokens,
    requestedOutputTokens,
  };
  for (const [name, value] of Object.entries(values)) {
    if (!Number.isInteger(value) || value <= 0) {
      throw new Error(`${name} must be a positive integer`);
    }
  }
  if (safeTotalTokens >= 4096) throw new Error("safeTotalTokens must stay below physical context 4096");
  if (safeInputTokens + minOutputTokens > safeTotalTokens) {
    throw new Error("safe input must preserve the minimum output reserve");
  }
  if (maxOutputTokens < minOutputTokens || maxOutputTokens >= safeTotalTokens) {
    throw new Error("invalid adaptive output range");
  }

  const requestInputCeiling = Math.min(safeInputTokens, safeTotalTokens - minOutputTokens);
  const blocked = guardInputTokens > requestInputCeiling;
  if (blocked) {
    return {
      blocked: true,
      requestInputCeiling,
      dynamicOutputCeiling: 0,
      outputReserve: 0,
      projectedTotalTokens: guardInputTokens,
    };
  }

  const dynamicOutputCeiling = Math.min(maxOutputTokens, safeTotalTokens - guardInputTokens);
  const outputReserve = Math.min(requestedOutputTokens, dynamicOutputCeiling);
  return {
    blocked: false,
    requestInputCeiling,
    dynamicOutputCeiling,
    outputReserve,
    projectedTotalTokens: guardInputTokens + outputReserve,
  };
}
