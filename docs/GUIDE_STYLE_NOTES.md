# Guide Style Notes

This file records the current design direction for the user guide so Codex or another assistant can continue working on it without needing the original chat history.

## Project context

- This is a **short-to-medium user guide (~25 pages)** for a game-related hobby project.
- The program is essentially a tool used in a modding-like workflow.
- The target audience is **nontechnical users**.
- The guide should feel **friendly, casual, and community-made**, not corporate or academic.
- The old guide was somewhat prose-heavy.
- The new version should keep useful explanatory prose, but make instructions easier to scan.
- Screenshots are expected to be an important part of the guide.

## Current design direction

Use **plain Typst rather than a full document template**.

The guide originally explored:
- `chribel`
- `basic-report`
- `min-manual`
- `min-book`

These were rejected as the main base for different reasons:

- **Chribel**: visually appealing, but its layout is fundamentally compact / documentation-note oriented, with narrow margins and a multi-column bias. Adapting it to a portrait, prose-heavy manual required too much template surgery.
- **Basic Report**: structurally appropriate, but even in compact mode it still felt too formal and professional for an amateur hobby project.
- **min-manual**: more technical/developer-oriented than necessary.
- **min-book**: more book-like than needed for a ~25-page guide.

The preferred approach is:

> **Plain Typst + Alertoni callouts + custom lightweight styling**

This gives enough structure without inheriting the personality of a large template.

## Typography

Current preferred font pairing:

- **Title / headings:** `Nunito Sans`
- **Body:** `Atkinson Hyperlegible Next`

Why:
- Nunito Sans feels friendly and polished without looking corporate.
- Atkinson Hyperlegible Next is highly readable and works well for instructions, UI labels, filenames, paths, and general prose.

Avoid making every text element Nunito Sans; the contrast between heading and body fonts helps the guide feel intentionally designed.

Suggested starting sizes:

- Main title: `28–30pt`, bold or extra-bold
- Level 1 headings: `18pt`, bold
- Level 2 headings: `13–14pt`, bold
- Body: `10.5pt`
- Subtitle: `12–13pt`

## Page layout

Suggested baseline:

```typst
#set page(
  paper: "a4",
  margin: (
    x: 18mm,
    y: 16mm,
  ),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Atkinson Hyperlegible Next",
  size: 10.5pt,
)

#set par(
  leading: 0.55em,
  justify: false,
)

#set heading(numbering: none)
```

Use a **single-column portrait layout**.

Do not use tightly packed margins or multi-column layouts.

## Heading styling

Suggested baseline:

```typst
#show heading.where(level: 1): it => block(
  above: 1.6em,
  below: 0.6em,
)[
  #text(
    font: "Nunito Sans",
    size: 18pt,
    weight: 700,
  )[
    #it.body
  ]
]

#show heading.where(level: 2): it => block(
  above: 1.3em,
  below: 0.45em,
)[
  #text(
    font: "Nunito Sans",
    size: 13.5pt,
    weight: 700,
  )[
    #it.body
  ]
]
```

Avoid numbered headings such as `2.1 Installation`.

Prefer:

- Getting Started
- Installation
- Using MyTool
- Installing Mods
- Common Problems

The guide should feel like a friendly manual rather than formal technical documentation.

## Title treatment

Prefer a simple title area instead of a formal cover page.

A left-aligned title is likely to fit the desired tone better than a centered report-style cover.

Example:

```typst
#text(
  font: "Nunito Sans",
  size: 30pt,
  weight: 800,
)[MyTool]

#v(0.15em)

#text(size: 13pt)[User Guide]

#v(1.8em)

This guide explains how to install and use MyTool.
```

Do not add corporate-style metadata such as:
- affiliation
- department
- report category
- formal author/date blocks

unless specifically needed.

## Callouts

Use the `alertoni` package.

```typst
#import "@preview/alertoni:1.0.0" as at
```

Callouts are useful for nontechnical readers, but should not overwhelm the page.

Keep the main categories simple:

- **Tip** — optional advice
- **Important** — something the user should definitely notice
- **Warning / Caution** — risk of breaking something, losing data, or causing a bad installation

Use `minimal` for most notes:

```typst
#at.callout(
  type: "tip",
  style: "minimal",
)[
  You only need to select the game folder the first time.
]
```

Use a stronger style such as `quarto` when something is genuinely important:

```typst
#at.callout(
  type: "warning",
  style: "quarto",
)[
  Do not close the program while files are being modified.
]
```

Avoid turning ordinary explanatory prose into callouts.

## Writing style

The guide can still contain prose.

Preferred pattern:

> **Prose explains → numbered steps instruct → screenshot confirms → callout highlights exceptions**

For example:

```typst
== Finding your game folder

MyTool needs to know where the game is installed before it can make changes.
You normally only need to set this once.

1. Open MyTool.
2. Select *Settings → Game Location*.
3. Click *Browse*.
4. Select the game's installation folder.

#figure(
  image("images/game-location.png", width: 90%),
  caption: [Selecting the game installation folder.],
)

#at.callout(type: "tip", style: "minimal")[
  If you installed the game through Steam, you can open the installation folder
  from Steam's *Manage → Browse local files* option.
]
```

Avoid dense walls of prose when a sequence is actually a procedure.

At the same time, do not reduce the guide to terse bullet points everywhere. Short explanatory paragraphs are useful for nontechnical readers.

## Screenshots and figures

Screenshots should be prominent and easy to read.

Typical usage:

```typst
#figure(
  image("images/example.png", width: 90%),
  caption: [The main MyTool window.],
)
```

Guidelines:
- Prefer large screenshots over tiny annotated thumbnails.
- Keep screenshots close to the instructions they support.
- Captions should explain what the user is looking at, not merely repeat the section title.
- Avoid excessive decorative framing.
- If annotations are added, keep them simple and readable.

## Overall visual goal

The guide should feel like:

- a polished README
- a good modding guide
- community documentation
- something made carefully by an enthusiast

It should **not** feel like:

- a corporate report
- an academic paper
- API documentation
- a dense cheat sheet
- a formal software manual from a large company

The visual design should remain intentionally modest.

## Current baseline skeleton

```typst
#import "@preview/alertoni:1.0.0" as at

#set document(
  title: [MyTool Guide],
)

#set page(
  paper: "a4",
  margin: (
    x: 18mm,
    y: 16mm,
  ),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Atkinson Hyperlegible Next",
  size: 10.5pt,
)

#set par(
  leading: 0.55em,
  justify: false,
)

#set heading(numbering: none)

#show heading.where(level: 1): it => block(
  above: 1.6em,
  below: 0.6em,
)[
  #text(
    font: "Nunito Sans",
    size: 18pt,
    weight: 700,
  )[
    #it.body
  ]
]

#show heading.where(level: 2): it => block(
  above: 1.3em,
  below: 0.45em,
)[
  #text(
    font: "Nunito Sans",
    size: 13.5pt,
    weight: 700,
  )[
    #it.body
  ]
]

#text(
  font: "Nunito Sans",
  size: 30pt,
  weight: 800,
)[MyTool]

#v(0.15em)

#text(size: 13pt)[User Guide]

#v(1.8em)

This guide explains how to install and use MyTool.

#at.callout(type: "tip", style: "minimal")[
  You don't need any modding experience to use this guide.
]

= Getting Started

...

= Installation

...

= Using MyTool

...

= Common Problems

...
```

## Guidance for future Codex work

When editing or extending this guide:

1. Preserve the casual hobby-project tone.
2. Do not introduce a large document template unless there is a strong reason.
3. Prefer small local style rules over framework-like abstractions.
4. Keep typography centered on Nunito Sans + Atkinson Hyperlegible Next.
5. Favor readability and screenshots over visual density.
6. Do not make the document look more corporate merely for the sake of polish.
7. Keep callouts purposeful.
8. When restructuring prose, preserve useful explanations while separating procedures into numbered steps.
9. Avoid unnecessary heading numbering.
10. Treat the current plain-Typst version as the visual baseline.
