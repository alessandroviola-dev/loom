import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { OUTPUT_RECOVERY_GUIDANCE, nextTruncationState } from "./policy.mjs";

export default function forgeLoomRuntimeHardening(pi: ExtensionAPI): void {
  let consecutiveLengthStops = 0;

  pi.on("agent_start", () => {
    consecutiveLengthStops = 0;
  });

  pi.on("before_agent_start", (event) => ({
    systemPrompt: `${event.systemPrompt}\n${OUTPUT_RECOVERY_GUIDANCE}`,
  }));

  pi.on("message_end", (event, ctx) => {
    if (event.message.role !== "assistant") return;

    const stopReason = event.message.stopReason;
    const state = nextTruncationState(consecutiveLengthStops, stopReason);
    consecutiveLengthStops = state.consecutive;

    if (!state.shouldAbort) return;

    if (ctx.hasUI) {
      ctx.ui.notify(
        "ForgeLoom stopped after two consecutive output truncations. Continue with smaller edit/write calls; identical retries are blocked by policy.",
        "warning",
      );
    }
    ctx.abort();
  });
}
