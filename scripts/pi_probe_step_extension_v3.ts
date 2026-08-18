import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const Params = Type.Object({});

export default function (pi: ExtensionAPI) {
  const target = Number(process.env.LOOM_PROBE_DEPTH ?? "1");
  let completed = 0;
  let callsThisTurn = 0;
  let blockedSameTurn = 0;

  pi.on("turn_start", async () => {
    callsThisTurn = 0;
  });

  pi.on("tool_call", async (event) => {
    if (event.toolName !== "probe_step") return;
    callsThisTurn += 1;
    if (callsThisTurn > 1) {
      blockedSameTurn += 1;
      return {
        block: true,
        reason: "LOOM probe allows exactly one probe_step call per model turn.",
        terminate: false,
      };
    }
  });

  pi.registerTool({
    name: "probe_step",
    label: "Probe Step",
    description:
      "Advance exactly one LOOM controlled multi-turn probe step. Call this tool at most once per model turn. After its result, follow CONTINUE or STOP exactly.",
    parameters: Params,

    async execute() {
      if (!Number.isInteger(target) || target < 1) {
        return {
          content: [{ type: "text", text: "PROBE_CONFIGURATION_ERROR" }],
          details: { advanced: false, completed, target, blockedSameTurn },
        };
      }

      completed += 1;
      const stop = completed >= target;
      return {
        content: [
          {
            type: "text",
            text: stop
              ? `STEP ${completed}/${target}\nSTOP. Reply exactly DONE and make no more tool calls.`
              : `STEP ${completed}/${target}\nCONTINUE. In the next model turn call probe_step exactly once.`,
          },
        ],
        details: {
          advanced: true,
          completed,
          target,
          stop,
          blockedSameTurn,
        },
      };
    },
  });
}
