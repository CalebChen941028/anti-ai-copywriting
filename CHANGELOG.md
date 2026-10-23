# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-10-23

### Added
- Integrated full `natural-voice` skill rules (Academic Voice, Controlled Plain Layer, Academic Presentation Standards, and full self-inspection checklist).
- Standalone zero-dependency Python linter `anti-ai-lint` with CLI supporting `--max-score`, `--format json|text`, and wordlist customization.
- Six fixture scenarios under `tests/fixtures/` with regression tests comparing before and after rewrites.
- Multi-agent adapter documentation for ZCode, Claude Code, Codex, OpenCode, Generic, and WorkBuddy.
- Bounded marker blocks for safe installation into shared rule files (`AGENTS.md`, `CLAUDE.md`).
- GitHub Actions CI workflow for Python 3.8-3.14.

### Changed
- Refined "不是……而是……" rule from blanket prohibition to targeting pseudo-contrasts without real empirical opposition (A3).
- Rewrote all English rule sections into idiomatic English (A4).
- Expanded bilingual forbidden buzzword lists with additional tropes and hedges (A2).
