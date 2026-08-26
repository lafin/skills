import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

type Level = "lite" | "full" | "ultra" | "off";

const LEVELS: Record<Level, true> = { lite: true, full: true, ultra: true, off: true };

let level: Level = "full";

const reminder = (lvl: Level) =>
  `<system-reminder>leancode ACTIVE, intensity ${lvl}. Reflexes: think before coding, simplicity first (YAGNI/reuse/stdlib/native/one line), surgical changes (every changed line traces to the request), goal-driven execution (one runnable check). Code first, then at most three lines: skipped X, add when Y. Full text: skill://leancode</system-reminder>`;

export default function leancode(pi: ExtensionAPI): void {
  pi.on("context", async (event) => {
    if (level === "off") return;
    return {
      messages: [
        ...event.messages,
        {
          role: "user",
          content: [{ type: "text", text: reminder(level) }],
          timestamp: Date.now(),
        },
      ],
    };
  });

  pi.registerCommand("leancode", {
    description: "Set leancode intensity: lite | full | ultra | off",
    handler: async (args, ctx) => {
      const next = String(args ?? "").trim().toLowerCase() as Level;
      if (!LEVELS[next]) {
        ctx.ui.notify(`leancode: ${level} (use lite|full|ultra|off)`, "info");
        return;
      }
      level = next;
      ctx.ui.setStatus("leancode", level === "off" ? "" : `lean:${level}`);
      ctx.ui.notify(`leancode ${level}`, "info");
    },
  });
}
