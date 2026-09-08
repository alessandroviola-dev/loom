export const OUTPUT_RECOVERY_GUIDANCE = [
  "ForgeLoom has a strict response budget. Tool-call arguments must fit inside it.",
  "Prefer small, targeted edit calls. For large changes, split the work into multiple independent edits instead of replacing a whole file in one call.",
  "Keep each edit/write payload compact (roughly <=1200 characters of changed text when practical). Re-read only the narrow region needed for the next edit.",
  "If a tool call is rejected because the response hit the output-token limit or its arguments were truncated, NEVER retry the same payload. Make the next tool call materially smaller.",
  "Do not create helper verification files unless the user explicitly requests them; use a short bash command for verification instead.",
].join("\n");

export function nextTruncationState(currentCount, stopReason) {
  const current = Number.isFinite(currentCount) && currentCount > 0 ? Math.trunc(currentCount) : 0;
  if (stopReason === "length") {
    const consecutive = current + 1;
    return { consecutive, shouldAbort: consecutive >= 2 };
  }
  return { consecutive: 0, shouldAbort: false };
}
