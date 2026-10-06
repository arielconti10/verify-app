# Feature map format

A feature map lists user-facing features and the recipe that proves each one.
Keep it next to the project procedure. Launch, health, capture, and cleanup commands stay in the procedure; the map links to them.

## Index

Write `features/README.md` with:

- A link to the project procedure and the shared state every recipe starts from.
- Map conventions that apply to every feature, such as preferred selectors or output flags.
- One line per feature file, naming the entry points it covers.

## Feature file

Start with an H1 title and one paragraph describing the user-visible behavior. Then use these four H2 sections in order:

1. `Sub-features`: short stable IDs, one line each. Prefix them with the feature, such as `tag-add`. Reports use these IDs.
2. `How to get to it (user POV)`: every user entry point, including shortcuts, menus, and commands.
3. `Driving it with <tool>`: a `Preconditions:` list, then one bullet per step. Each bullet pairs the user action with the exact command and the observable result.
4. `Gotchas`: traps that waste or invalidate a run. Add new ones when a run finds them.

Name user paths, stable handles, required state, commands, and observable results. Leave implementation details out.

## Example

```markdown
# Tag a bookmark

A user adds or removes tags on a saved bookmark and filters the list by tag, from the web app or the `marks` CLI.

## Sub-features

- `tag-add` adds a tag from the bookmark detail panel.
- `tag-remove` removes a tag and keeps the bookmark.
- `tag-filter` shows only bookmarks with the chosen tag.
- `tag-cli` adds a tag from the terminal.

## How to get to it (user POV)

- Open a bookmark and use the `Tags` field in the detail panel.
- Choose a tag chip in the sidebar to filter.
- Run `marks tag <id> <tag>` in a terminal.

## Driving it with agent-browser and the shell

Preconditions:

- The procedure's health check passes for the seeded data set.
- Bookmark `Rust book` exists and has no tags.

- **Add tag.** Open `Rust book`, type `reading` in the `Tags` combobox, and press Enter. A chip named `reading` appears in the panel.
- **Persistence.** Reload and reopen `Rust book`. The `reading` chip remains.
- **Filter.** Choose `reading` in the sidebar. The list shows `Rust book` and no untagged bookmarks.
- **Remove tag.** Choose `Remove reading` on the chip. The chip disappears and `Rust book` stays in `All bookmarks`.
- **CLI.** Run `marks tag 42 later --json`. Exit code `0`; stdout lists `later` in the bookmark's tags.
- **Proof.** Capture the filtered list with the procedure's capture command, then run its validation check.

## Gotchas

- Tags are lowercased on save. Assert the rendered chip, not the typed value.
- The sidebar count updates after a short delay. Wait for the count, not a fixed sleep.
- The CLI prints a table by default. Use `--json` for assertions.
```
