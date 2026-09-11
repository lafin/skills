import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

type Level = "lite" | "full" | "ultra" | "off";

const DEFAULT_LEVEL: Level = "full";
const LEVELS: Record<Level, true> = { lite: true, full: true, ultra: true, off: true };
const STATE_MARKER = "[omp:leancode-state]";
const STATE_PREFIX = `<system-reminder>${STATE_MARKER} `;
const STATE_SUFFIX = " Full text: skill://leancode</system-reminder>";
const ACTIVE_INSTRUCTIONS: Record<Exclude<Level, "off">, string> = {
  lite: "Apply the four reflexes. Build exactly what was asked; name the leaner alternative in one line and let the user decide.",
  full: "Apply the four reflexes. Prefer reuse, stdlib, and native features; use the shortest working diff and explanation; leave one runnable check.",
  ultra: "Apply the four reflexes as a YAGNI extremist: delete before adding, ship the smallest working solution, and challenge excess requirements.",
};
const LEGACY_REMINDERS: Record<string, true> = {
  [`${STATE_PREFIX}Leancode is ACTIVE at lite intensity. Apply the four reflexes. Build exactly what was asked; name the leaner alternative in one line and let the user decide. Code first, then at most three lines.${STATE_SUFFIX}`]: true,
  [`${STATE_PREFIX}Leancode is ACTIVE at full intensity. Apply the four reflexes. Prefer reuse, stdlib, and native features; use the shortest working diff and explanation; leave one runnable check. Code first, then at most three lines.${STATE_SUFFIX}`]: true,
  [`${STATE_PREFIX}Leancode is ACTIVE at ultra intensity. Apply the four reflexes as a YAGNI extremist: delete before adding, ship the smallest working solution, and challenge excess requirements. Code first, then at most three lines.${STATE_SUFFIX}`]: true,
  [`${STATE_PREFIX}Leancode is OFF. Do not apply leancode instructions. This current state overrides older leancode reminders. Re-enable with /leancode lite, /leancode full, or /leancode ultra.${STATE_SUFFIX}`]: true,
};

let level: Level = DEFAULT_LEVEL;

export function leancodeReminder(level: Level): string {
  const instruction =
    level === "off"
      ? "Leancode is OFF. Do not apply leancode instructions. This current state overrides older leancode reminders. Re-enable with /leancode lite, /leancode full, or /leancode ultra."
      : `Leancode is ACTIVE at ${level} intensity. ${ACTIVE_INSTRUCTIONS[level]} Code first, then at most three lines.`;
  return `${STATE_PREFIX}${instruction}${STATE_SUFFIX}`;
}

function isLevel(value: string): value is Level {
  return Object.hasOwn(LEVELS, value);
}

function isLeancodeStateMessage(message: unknown): boolean {
  if (!message || typeof message !== "object" || !("role" in message) || message.role !== "user") return false;
  if (!("content" in message) || !Array.isArray(message.content) || message.content.length !== 1) return false;
  const [part] = message.content;
  if (
    !part ||
    typeof part !== "object" ||
    !("type" in part) ||
    part.type !== "text" ||
    !("text" in part) ||
    typeof part.text !== "string"
  ) {
    return false;
  }
  const attribution = "attribution" in message ? message.attribution : undefined;
  return (
    (attribution === "agent" &&
      part.text.startsWith(STATE_PREFIX) &&
      part.text.endsWith(STATE_SUFFIX)) ||
    (attribution === undefined && Object.hasOwn(LEGACY_REMINDERS, part.text))
  );
}

export default function leancode(pi: ExtensionAPI): void {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.setStatus("leancode", `lean:${level}`);
  });

  pi.on("context", async (event) => ({
    messages: [
      ...event.messages.filter(message => !isLeancodeStateMessage(message)),
      {
        role: "user",
        attribution: "agent",
        content: [{ type: "text", text: leancodeReminder(level) }],
        timestamp: Date.now(),
      },
    ],
  }));

  pi.registerCommand("leancode", {
    description: "Set leancode intensity: lite | full | ultra | off",
    handler: async (args, ctx) => {
      const next = String(args ?? "").trim().toLowerCase();
      if (!isLevel(next)) {
        ctx.ui.notify(`leancode: ${level} (use lite|full|ultra|off)`, "info");
        return;
      }
      level = next;
      ctx.ui.setStatus("leancode", `lean:${level}`);
      ctx.ui.notify(`leancode ${level}`, "info");
    },
  });
}
