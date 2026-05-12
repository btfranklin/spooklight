# UI Implementation Guidance

Use this guide whenever changing Spooklight templates, styles, or user-facing interaction flows.

## Product Shape

Spooklight is a creative workspace, not a marketing site or generic admin panel. UI should feel quiet, direct, and useful for repeated worldbuilding work.

Prefer screens that help the user inspect, create, and continue work quickly. Avoid decorative explanation, feature tours, and generic SaaS filler inside authenticated product surfaces.

Do not add extra text or exposition to UI elements. UI elements should be minimal and contain only the elements requested.

## Layout

- Keep the header stable across public and authenticated surfaces.
- Put the primary workflow on the page directly; do not hide core actions behind ornamental panels.
- Use generous visual space for world cards and world imagery, but keep metadata compact and readable.
- Prefer clear sections with direct headings over nested card stacks.
- Preserve mobile readability before adding dense desktop-only treatments.

## Visual Language

- World cards should feel like windows into worlds: image-led, large, and atmospheric.
- Use image backgrounds when they represent real world state or accepted/generated artifacts.
- Use restrained overlays only to preserve text readability.
- Use `$integrate-daisyui-into-django` when changing DaisyUI/Tailwind setup, custom theme tokens, reusable component patterns, or when a DaisyUI component does not render as expected.
- Do not add decorative badges, pills, chips, labels, or tag-like UI unless the user specifically requests them.
- In particular, do not add badges for genre, status, or empty-state markers such as "Riverpunk" or "No cover yet" by default.
- If metadata is useful, render it as normal text, a definition list, or a compact metadata row.

## Copy

- Keep authenticated UI copy practical and specific.
- Do not add explanatory UI text unless the user requested it or the interface would otherwise be ambiguous.
- Avoid explaining implementation details to users unless the state directly affects them.
- Empty states should tell the user what they can do next without over-describing future features.
- Error states should be plain, recoverable, and tied to the action that failed.

## Controls

- Use normal buttons and links for clear commands.
- Keep form fields close to the concepts users are authoring.
- Prefer explicit labels and helper text over clever phrasing.
- For destructive or externally visible actions, require a clear user action and confirmation where appropriate.
- For AI tasks, show a small spinner while work is queued or running and poll an owner-scoped status fragment until the task reaches a terminal state.
- Do not expose queue internals, worker names, task IDs, or provider IDs in normal product UI unless specifically requested.

## Validation

After UI changes, run:

```sh
pdm run lint
npm run build:css
docker compose up -d --build
```

Rebuild the Docker containers after UI changes so template and asset changes are picked up by the running preview stack.

For behavior-changing UI, also run:

```sh
pdm run test
```
