---
name: journal
description: Capture an explanation, note, or summary into the user's Obsidian knowledge vault (~/journal on Linux, ~/Desktop/journal on Mac). Use when the user asks to write/save/capture/record something to the vault, journal, or knowledge base — especially phrasings like "write this to the vault" or "add this to my journal". Dispatches the journal-scribe subagent in the background so work in the current repo continues immediately.
metadata:
  short-description: Capture knowledge into the Obsidian vault (background)
---

# Journal

## Overview

Persist knowledge into the user's Obsidian vault WITHOUT blocking current work, by delegating to the `journal-scribe` subagent. That agent resolves the host-specific vault path, obeys the vault's `CLAUDE.md`, finds-or-creates the right note, wires `[[wikilinks]]`, and never hard-wraps Markdown — so this skill is only the trigger and dispatch.

## Steps

1. Determine WHAT to capture. The topic/target comes from the user's arguments (`$ARGUMENTS`) if given. For the content: if the user refers to "this/that explanation", use the relevant recent assistant explanation from the conversation (rendered as clean note prose — single-line paragraphs, no hard-wrap); otherwise use the content they specify.
2. Launch the `journal-scribe` agent via the Agent tool with `run_in_background: true`, passing the content to capture plus any target hint (note / section / folder) and the instruction to find-or-create the right home. Do not pre-resolve the vault path or conventions — the agent handles those.
3. Tell the user in one line that it is dispatched, then continue with whatever they were doing. When the background agent completes, relay its report (path, created-vs-appended, tags, links).

## Notes

- Always run in the background — the entire point is to not block substantive development or analysis.
- Do not reimplement the agent's logic here; this skill just gathers the content and dispatches.
- If `journal-scribe` is unavailable, fall back to a general-purpose agent given the same instructions (resolve the vault path, obey the vault CLAUDE.md, no hard-wrapping, find-or-create, wire links, don't commit).
