// Status: Reusable. mode_smoke.py loads this with the leancode hook to record what each
// `context` event receives, so the smoke can assert that no earlier reminder persists.
import { appendFileSync } from "node:fs";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

export default function leancodeContextProbe(pi: ExtensionAPI): void {
  pi.on("context", async event => {
    const path = process.env.LEANCODE_CONTEXT_PROBE;
    if (!path) return;
    const reminderIndexes = event.messages.flatMap((message, index) =>
      JSON.stringify(message).includes("[omp:leancode-state] Leancode is") ? [index] : [],
    );
    appendFileSync(path, `${JSON.stringify({ messages: event.messages.length, reminderIndexes })}\n`);
  });
}
