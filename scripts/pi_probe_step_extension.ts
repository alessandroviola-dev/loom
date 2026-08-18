import { randomBytes } from "node:crypto";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const Params = Type.Object({
  token: Type.String({ description: "Exact opaque token from the previous probe step" }),
});

export default function (pi: ExtensionAPI) {
  const target = Number(process.env.LOOM_PROBE_DEPTH ?? "1");
  const initial = process.env.LOOM_PROBE_INITIAL_TOKEN ?? "";

  let completed = 0;
  let expected = initial;

  pi.registerTool({
    name: "probe_step",
    label: "Probe Step",
    description:
      "Advance exactly one LOOM memory-probe step. Use only the exact token supplied by the prompt or immediately preceding probe_step result. Never guess a token.",
    parameters: Params,

    async execute(_toolCallId, params) {
      if (!Number.isInteger(target) || target < 1) {
        return {
          content: [{ type: "text", text: "PROBE_CONFIGURATION_ERROR" }],
          details: { advanced: false, completed, target },
        };
      }

      if (params.token !== expected) {
        return {
          content: [
            {
              type: "text",
              text: "INVALID_TOKEN. State did not advance. Use only the exact token most recently supplied by the probe.",
            },
          ],
          details: { advanced: false, completed, target },
        };
      }

      completed += 1;

      if (completed >= target) {
        expected = "";
        return {
          content: [{ type: "text", text: `STEP ${completed}/${target}\nSTOP` }],
          details: { advanced: true, completed, target, stop: true },
        };
      }

      expected = randomBytes(16).toString("hex");
      return {
        content: [
          {
            type: "text",
            text: `STEP ${completed}/${target}\nNEXT_TOKEN: ${expected}`,
          },
        ],
        details: { advanced: true, completed, target, stop: false },
      };
    },
  });
}
