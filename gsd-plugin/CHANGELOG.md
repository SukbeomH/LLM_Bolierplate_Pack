# Changelog

## [1.0.0](https://github.com/SukbeomH/LLM_Bolierplate_Pack/releases/tag/gsd-plugin-v1.0.0) (2026-01-29)

### Features

* Initial release of GSD Plugin for Claude Code
* 31 slash commands for GSD workflow
* 14 skills for development automation
* 13 specialized agents
* Hook system (SessionStart, PreToolUse, PostToolUse, PreCompact, Stop, SessionEnd)
* MCP server integration (graph-code, memorygraph)
* GSD document templates (22 templates)

### Components

**Commands:**
- `/gsd:init`, `/gsd:plan`, `/gsd:execute`, `/gsd:verify`
- `/gsd:debug`, `/gsd:map`, `/gsd:progress`, `/gsd:resume`, `/gsd:pause`
- `/gsd:new-project`, `/gsd:new-milestone`, `/gsd:complete-milestone`
- And 19 more commands...

**Skills:**
- commit, create-pr, pr-review, clean, planner, plan-checker
- executor, verifier, debugger, impact-analysis, arch-review
- codebase-mapper, context-health-monitor, empirical-validation, bootstrap

**Agents:**
- planner, plan-checker, executor, verifier, debugger, clean
- commit, create-pr, pr-review, impact-analysis, arch-review
- codebase-mapper, context-health-monitor
