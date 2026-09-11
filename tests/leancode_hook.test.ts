import { describe, expect, test } from "bun:test";
import leancode, { leancodeReminder } from "../.omp/hooks/pre/leancode";

const MARKER = "[omp:leancode-state]";
const LEGACY_FULL_REMINDER =
  "<system-reminder>[omp:leancode-state] Leancode is ACTIVE at full intensity. Apply the four reflexes. Prefer reuse, stdlib, and native features; use the shortest working diff and explanation; leave one runnable check. Code first, then at most three lines. Full text: skill://leancode</system-reminder>";
const LEGACY_ULTRA_REMINDER =
  "<system-reminder>[omp:leancode-state] Leancode is ACTIVE at ultra intensity. Apply the four reflexes as a YAGNI extremist: delete before adding, ship the smallest working solution, and challenge excess requirements. Code first, then at most three lines. Full text: skill://leancode</system-reminder>";

type Callback = (...args: unknown[]) => Promise<unknown>;

function loadHook(extension = leancode) {
  const handlers: Record<string, Callback | undefined> = {};
  let command: Callback | undefined;
  const statuses: Array<[string, string | undefined]> = [];
  const notifications: Array<[string, string | undefined]> = [];
  const apiShape = {
    on(name: string, handler: Callback) {
      handlers[name] = handler;
    },
    registerCommand(name: string, definition: { handler: Callback }) {
      expect(name).toBe("leancode");
      command = definition.handler;
    },
  };
  // The test double intentionally implements only the two registration methods used by this hook.
  const api = apiShape as unknown as Parameters<typeof leancode>[0];
  const context = {
    ui: {
      setStatus(key: string, value: string | undefined) {
        statuses.push([key, value]);
      },
      notify(message: string, type?: string) {
        notifications.push([message, type]);
      },
    },
  };
  const callback = (name: string): Callback => {
    const registered = handlers[name];
    if (!registered) throw new Error(`Missing ${name} handler`);
    return registered;
  };

  extension(api);

  return {
    statuses,
    notifications,
    start: () => callback("session_start")({}, context),
    setMode: (mode: string) => {
      if (!command) throw new Error("Missing leancode command");
      return command(mode, context);
    },
    apply: async (messages: unknown[] = []) => {
      const result = await callback("context")({ messages }, context);
      if (!result || typeof result !== "object" || !("messages" in result) || !Array.isArray(result.messages)) {
        throw new Error("Context handler did not return messages");
      }
      return { messages: result.messages };
    },
  };
}

function markedTexts(messages: unknown[]): string[] {
  return messages.flatMap(message => {
    if (!message || typeof message !== "object" || !("role" in message) || message.role !== "user") return [];
    if (!("content" in message) || !Array.isArray(message.content)) return [];
    return message.content.flatMap(part => {
      if (!part || typeof part !== "object" || !("type" in part) || part.type !== "text") return [];
      if (!("text" in part) || typeof part.text !== "string" || !part.text.includes(MARKER)) return [];
      return [part.text];
    });
  });
}

describe("leancode hook state", () => {
  test("reminders distinguish every active intensity and explicit off", () => {
    for (const mode of ["lite", "full", "ultra"] as const) {
      expect(leancodeReminder(mode)).toContain(`ACTIVE at ${mode}`);
    }
    expect(leancodeReminder("off")).toContain("Leancode is OFF");
    expect(leancodeReminder("off")).toContain("Do not apply leancode instructions");
  });

  test("all modes update context, status, and notification", async () => {
    const hook = loadHook();
    await hook.start();
    expect(hook.statuses).toEqual([["leancode", "lean:full"]]);

    let result = await hook.apply([]);
    expect(markedTexts(result.messages)).toHaveLength(1);
    expect(markedTexts(result.messages)[0]).toContain("ACTIVE at full");
    const injected = result.messages.at(-1);
    expect(injected && typeof injected === "object" && "attribution" in injected && injected.attribution).toBe("agent");

    for (const mode of ["lite", "ultra", "off", "full"] as const) {
      await hook.setMode(mode);
      result = await hook.apply(result.messages);
      const reminders = markedTexts(result.messages);
      expect(reminders).toHaveLength(1);
      expect(reminders[0]).toContain(mode === "off" ? "Leancode is OFF" : `ACTIVE at ${mode}`);
    }

    expect(hook.statuses).toEqual([
      ["leancode", "lean:full"],
      ["leancode", "lean:lite"],
      ["leancode", "lean:ultra"],
      ["leancode", "lean:off"],
      ["leancode", "lean:full"],
    ]);
    expect(hook.notifications).toEqual([
      ["leancode lite", "info"],
      ["leancode ultra", "info"],
      ["leancode off", "info"],
      ["leancode full", "info"],
    ]);
  });

  test("replaces all stale generated reminders and preserves other messages", async () => {
    const hook = loadHook();
    const keep = { role: "user", content: [{ type: "text", text: "keep me" }], timestamp: 1 };
    const stale = (mode: Parameters<typeof leancodeReminder>[0]) => ({
      role: "user",
      attribution: "agent",
      content: [{ type: "text", text: leancodeReminder(mode) }],
      timestamp: 2,
    });
    const legacy = {
      role: "user",
      content: [{ type: "text", text: LEGACY_ULTRA_REMINDER }],
      timestamp: 3,
    };

    await hook.setMode("off");
    const result = await hook.apply([legacy, stale("full"), keep, stale("off")]);

    expect(result.messages).toContain(keep);
    expect(markedTexts(result.messages)).toEqual([leancodeReminder("off")]);
    await hook.setMode("full");
  });

  test("preserves a user message that mentions the state marker", async () => {
    const hook = loadHook();
    const mention = {
      role: "user",
      content: [{ type: "text", text: `Please explain "${MARKER}" without changing this message.` }],
      timestamp: 1,
    };

    await hook.setMode("full");
    const result = await hook.apply([mention]);

    expect(result.messages).toContain(mention);
    expect(markedTexts(result.messages)).toEqual([mention.content[0].text, leancodeReminder("full")]);
  });

  test("preserves an attributed user copy of an exact reminder", async () => {
    const hook = loadHook();
    const copy = {
      role: "user",
      attribution: "user",
      content: [{ type: "text", text: LEGACY_FULL_REMINDER }],
      timestamp: 1,
    };

    await hook.setMode("full");
    const result = await hook.apply([copy]);

    expect(result.messages).toContain(copy);
    expect(markedTexts(result.messages)).toEqual([LEGACY_FULL_REMINDER, leancodeReminder("full")]);
  });

  test("preserves an unattributed user message that only resembles a reminder", async () => {
    const hook = loadHook();
    const copy = {
      role: "user",
      content: [
        {
          type: "text",
          text: `<system-reminder>${MARKER} user-authored content Full text: skill://leancode</system-reminder>`,
        },
      ],
      timestamp: 1,
    };

    const result = await hook.apply([copy]);

    expect(result.messages).toContain(copy);
    expect(markedTexts(result.messages)).toEqual([copy.content[0].text, leancodeReminder("full")]);
  });

  test("invalid input reports the current mode without changing it", async () => {
    const hook = loadHook();
    await hook.start();
    await hook.setMode("constructor");
    const result = await hook.apply([]);

    expect(hook.statuses).toEqual([["leancode", "lean:full"]]);
    expect(hook.notifications).toEqual([["leancode: full (use lite|full|ultra|off)", "info"]]);
    expect(markedTexts(result.messages)[0]).toContain("ACTIVE at full");
  });

  test("mode persists across in-process hook instances", async () => {
    const firstSession = loadHook();
    await firstSession.setMode("off");

    const nextSession = loadHook();
    await nextSession.start();

    expect(nextSession.statuses).toEqual([["leancode", "lean:off"]]);
    expect(markedTexts((await nextSession.apply([])).messages)[0]).toContain("Leancode is OFF");
    await firstSession.setMode("full");
  });

  test("a fresh process defaults to full", async () => {
    const firstProcess = loadHook();
    await firstProcess.setMode("off");
    expect(markedTexts((await firstProcess.apply([])).messages)[0]).toContain("Leancode is OFF");

    // A distinct module instance has the same clean state as a restarted process.
    const restartedModule = await import("../.omp/hooks/pre/leancode.ts?restart-default");
    const restartedProcess = loadHook(restartedModule.default);
    await restartedProcess.start();
    expect(restartedProcess.statuses).toEqual([["leancode", "lean:full"]]);
    expect(markedTexts((await restartedProcess.apply([])).messages)[0]).toContain("ACTIVE at full");
    await firstProcess.setMode("full");
  });
});
