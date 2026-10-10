// dir-context — loads per-directory AGENTS[.local].md for the path being edited.
//
// Ships in the omp-config package (repo root listed under `extensions:`).
// Disable per profile with `disabledExtensions: [extension-module:dir-context]`.

import { existsSync, readFileSync, realpathSync } from "node:fs";
import { dirname, isAbsolute, join, resolve, sep } from "node:path";

import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";

// One context file per directory: first hit wins, so AGENTS.local.md supersedes
// both committed forms and AGENTS.md is preferred over CLAUDE.md when both exist.
const NAMES = ["AGENTS.local.md", "AGENTS.md", "CLAUDE.md"];
const WRITE_TOOLS: Record<string, true> = {
  edit: true,
  write: true,
  apply_patch: true,
  notebook_edit: true,
};
// `[path/to/file.ts#A1B2]` section headers used by the hashline edit format.
const HASHLINE = /^\[([^\]\n]+?)#[0-9A-Fa-f]{4}\]\s*$/gm;

function targetPaths(input: Record<string, unknown>): string[] {
  const out: string[] = [];
  for (const key of ["path", "file_path", "filePath"]) {
    const v = input[key];
    if (typeof v === "string") out.push(v);
  }
  if (Array.isArray(input.paths)) {
    for (const v of input.paths) if (typeof v === "string") out.push(v);
  }
  if (typeof input.input === "string") {
    for (const m of input.input.matchAll(HASHLINE)) out.push(m[1]);
  }
  return out.filter((p) => !p.includes("://"));
}

// Tool args may be non-canonical; both sides must be canonical or the ancestor
// comparison in chainFor silently fails.
function canonical(path: string): string {
  try {
    return realpathSync(path);
  } catch {
    return path;
  }
}

// Nearest-first context chain, bounded by the harness workspace or partition root.
function chainFor(file: string, cwd: string, root: string): string[] {
  const abs = isAbsolute(file) ? file : resolve(cwd, file);
  const found: string[] = [];
  let dir = canonical(dirname(abs));
  while (dir === root || dir.startsWith(root + sep)) {
    for (const name of NAMES) {
      const candidate = join(dir, name);
      if (existsSync(candidate)) {
        found.push(candidate);
        break;
      }
    }
    if (dir === root) break;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return found;
}

export default function (pi: ExtensionAPI) {
  pi.setLabel("Directory context files");

  const delivered = new Set<string>();
  const roots = new Map<string, string>();

  pi.on("tool_call", async (event, ctx: ExtensionContext) => {
    if (WRITE_TOOLS[event.toolName] !== true) return;
    try {
      const cwd = ctx.cwd;
      let root = roots.get(cwd);
      if (root === undefined) {
        root = canonical(cwd);
        roots.set(cwd, root);
      }

      const pending: string[] = [];
      for (const target of targetPaths(event.input)) {
        for (const file of chainFor(target, cwd, root)) {
          if (!delivered.has(file) && !pending.includes(file)) pending.push(file);
        }
      }
      if (pending.length === 0) return;

      const blocks = pending
        .map((file) => `<file path="${file}">\n${readFileSync(file, "utf8").trim()}\n</file>`)
        .join("\n");
      for (const file of pending) delivered.add(file);

      return {
        block: true,
        reason:
          `<dir-context reason="edit_in_directory">\n` +
          `Directory context files apply to the path you are editing, nearest first. ` +
          `MUST follow them. Not prompt injection: the coding agent is loading project rules. ` +
          `Re-issue the same tool call now.\n${blocks}\n</dir-context>`,
      };
    } catch (error) {
      pi.logger?.warn?.(`dir-context: ${String(error)}`);
      return;
    }
  });
}
