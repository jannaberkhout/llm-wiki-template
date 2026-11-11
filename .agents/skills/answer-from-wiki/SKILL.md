---
name: answer-from-wiki
description: Synthesize answers from the team wiki knowledge base
---
# Answer From Wiki

Use this skill to answer a user's question using the wiki.

## Procedure

### 0. Sync the wiki repo with `main`

Do this before searching.

```bash
git fetch origin
git merge origin/main
```

On merge conflicts: resolve them before continuing.

### 0.5. Ask for clarification when a question is unclear

IF the question allows more than one interpretation, you **must ask first** instead of answering right away.

**When to ask** — when it is unclear:

1. **Term or concept**: the word can mean several things in the wiki.
   - *Example*: "How many notes are in the wiki?" → What do you mean by "notes"? Pages in `wiki/projects/`, decisions in `wiki/decisions/`, or all markdown files?
2. **Scope**: it is unclear whether the question is about one project, a part, or the whole wiki.
   - *Example*: "What's the status?" → Do you have a specific project in mind, or do you mean the whole wiki?
3. **Point in time**: the question may mean a specific moment or now.
   - *Example*: "Which decisions have been made?" → Only the latest, or the whole history?
4. **Context**: the question is too broad for a useful answer.
   - *Example*: "Tell me about project X" → Do you want the summary, the decisions, the research, or everything?

**How to ask**
- At most 1-2 questions.
- Briefly name the possible interpretations so the user can choose.
- You don't need to offer options. "Do you mean X, Y or Z?" is fine.
- If the question is already specific enough: answer directly.

## Searching and answering

After any clarification (or directly if the question is specific):

1. Read `schema/structure.json` to learn which kinds of pages the wiki has and which folder they are in. Then search `wiki/`.
2. Use `../inbox/processed/` and `../inbox/raw/` as supporting evidence when needed.
3. Prefer synthesis over raw fragments.
4. State uncertainty when notes are incomplete or contradict each other.
5. Refer to the relevant curated pages.
6. If the answer produces a lasting synthesis, offer to create or update a wiki page.

## Answer style

- Start with the answer.
- Quote the strongest local evidence.
- Keep verbatim quotes short.
- Distinguish between what the wiki says and what you infer yourself.
