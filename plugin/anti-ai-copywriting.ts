// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Liangliang Chen
/**
 * OpenCode In-Loop Verification Plugin for Anti-AI Copywriting (Harness² c8 Paradigm)
 *
 * Intercepts tool file writes (`write_to_file`, `replace_file_content`, etc.),
 * runs `anti-ai-lint` on drafted prose, and injects actionable agent feedback
 * whenever machine clichés, buzzwords, or hedging are detected.
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import * as path from "node:path";

const execFileAsync = promisify(execFile);

export interface ToolExecutionEvent {
  toolName: string;
  args: Record<string, any>;
  result?: any;
}

export interface LintHookResult {
  passed: boolean;
  score: number;
  output: string;
  feedback?: string;
}

const SUPPORTED_EXTENSIONS = new Set([".md", ".markdown", ".txt"]);

export async function runAntiAiLint(
  filePath: string,
  genre: "general" | "academic" | "plain" = "general",
  maxScore: number = 10.0
): Promise<LintHookResult> {
  const pluginDir = typeof __dirname !== "undefined" ? __dirname : process.cwd();
  const candidateLint = path.resolve(pluginDir, "lint");
  const parentLint = path.resolve(pluginDir, "../lint");
  const resolvedLint = [candidateLint, parentLint].join(path.delimiter);
  const pythonPath = process.env.PYTHONPATH
    ? `${resolvedLint}${path.delimiter}${process.env.PYTHONPATH}`
    : resolvedLint;

  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-m",
        "anti_ai_lint.cli",
        filePath,
        "--genre",
        genre,
        "--format",
        "agent",
        "--max-score",
        maxScore.toString(),
      ],
      {
        env: {
          ...process.env,
          PYTHONPATH: pythonPath,
        },
      }
    );

    return {
      passed: true,
      score: 0.0,
      output: stdout,
    };
  } catch (error: any) {
    const stdout = (error?.stdout ?? "").toString().trim();
    const stderr = (error?.stderr ?? error?.message ?? "").toString().trim();
    if (stdout.includes("<anti-ai-lint-feedback")) {
      return {
        passed: false,
        score: 1.0,
        output: stdout,
        feedback: stdout,
      };
    }
    return {
      passed: false,
      score: 1.0,
      output: stderr,
      feedback: stdout || stderr || "Prose failed anti-ai-lint verification.",
    };
  }
}

const WRITE_TOOLS = new Set([
  "write_to_file",
  "replace_file_content",
  "apply_diff",
  "edit_file",
  "write_file",
  "create_file",
  "append_to_file",
  "patch_file",
]);

/**
 * OpenCode postToolExecution hook listener.
 */
export async function postToolExecution(event: ToolExecutionEvent): Promise<string | null> {
  if (event.toolName && !WRITE_TOOLS.has(event.toolName.toLowerCase())) {
    return null;
  }

  const fileTarget =
    event.args?.TargetFile ||
    event.args?.filePath ||
    event.args?.file_path ||
    event.args?.target_file ||
    event.args?.path ||
    event.args?.target ||
    event.args?.Target;

  if (!fileTarget || typeof fileTarget !== "string") {
    return null;
  }

  const ext = path.extname(fileTarget).toLowerCase();
  if (!SUPPORTED_EXTENSIONS.has(ext)) {
    return null;
  }

  // Detect genre from path if possible, default to general
  const isAcademic = fileTarget.includes("paper") || fileTarget.includes("academic");
  const isPlain = fileTarget.includes("guide") || fileTarget.includes("doc");
  const genre = isAcademic ? "academic" : isPlain ? "plain" : "general";

  const result = await runAntiAiLint(fileTarget, genre);
  if (!result.passed && result.feedback) {
    return result.feedback;
  }

  return null;
}

export default {
  name: "anti-ai-copywriting",
  version: "0.3.0",
  description: "Deterministic in-loop prose quality gate for OpenCode agents.",
  postToolExecution,
};
