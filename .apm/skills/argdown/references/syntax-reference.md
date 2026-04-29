# Argdown Syntax Reference

Complete reference for the Argdown markup language.

## Contents

- [Statements](#statements)
- [Equivalence Classes (Titled Statements)](#equivalence-classes-titled-statements)
- [Arguments](#arguments)
- [Relations](#relations)
- [Premise-Conclusion Structures (PCS)](#premise-conclusion-structures-pcs)
- [Headings](#headings)
- [Tags](#tags)
- [Metadata / Data Flags](#metadata--data-flags)
- [Frontmatter Configuration](#frontmatter-configuration)
- [Comments](#comments)
- [Bold and Italic Text](#bold-and-italic-text)
- [Links](#links)
- [Shortcodes (Unicode Symbols & Emojis)](#shortcodes-unicode-symbols--emojis)

## Statements

Statements are paragraphs of text separated by empty lines — the basic building blocks of Argdown.

```argdown
This is a statement.

This is another statement. It spans
multiple lines without an empty line break.

A third statement begins after the empty line above.
```

- Each paragraph is a distinct statement
- A statement is a **non-repeatable string occurrence** at a specific location
- Copy-pasting creates a new, separate statement

## Equivalence Classes (Titled Statements)

Group statements by assigning titles in `[Square Brackets]`:

```argdown
[Censorship]: Censorship is not wrong in principle.

[Freedom of Speech]: Freedom of speech is an absolute right.

// Reference the same equivalence class later:
[Censorship]: Restating the censorship position from a different angle.
```

- `[Title]: text` defines/references an equivalence class
- All statements with the same title share the same equivalence class
- Equivalence classes are how Argdown tracks "the same proposition" across the document
- A titled statement without a colon is a **reference**: `[Title]`

## Arguments

Arguments are titled with `<Angle Brackets>`:

```argdown
<Teleological Proof>: Since the world is
  intelligently designed, there has to be
  an intelligent creator.
```

- **Definition**: `<Title>: informal description` (with colon and text)
- **Reference**: `<Title>` (without colon — just the title)
- Argument descriptions are NOT statements — they don't belong to equivalence classes
- Arguments can have premise-conclusion structures (PCS)

## Relations

Relations connect elements. They appear **indented below** a parent element:

```argdown
[Main Thesis]: The central claim.
  +> [Supported Statement]     // outgoing support
  -> [Attacked Statement]      // outgoing attack
  <+ [Supporting Evidence]     // incoming support
  <- [Counter Evidence]        // incoming attack
  _> <Undercut Target>         // undercut (targets an inference)
  <_ <Source of Undercut>      // undercut by
```

### All Relation Symbols

| Symbol | Direction | Loose Mode Meaning | Strict Mode Meaning |
|--------|-----------|-------------------|---------------------|
| `+>` | Outgoing | Supports | Entails |
| `->` | Outgoing | Attacks | Is contrary to |
| `_>` | Outgoing | Undercuts | Undercuts |
| `<+` | Incoming | Is supported by | Is entailed by |
| `<-` | Incoming | Is attacked by | Is contrary to |
| `<_` | Incoming | Is undercut by | Is undercut by |
| `><` | Symmetric | *(not available)* | Contradicts |

### Relations between different element types

```argdown
// Statement-to-statement
[A]: Claim A.
  +> [B]
  -> [C]

// Argument-to-statement
<Arg1>: Supports the thesis.
  +> [Main Thesis]

// Statement-to-argument
[Evidence]: Key evidence.
  +> <Arg1>

// Argument-to-argument
<Arg1>: First argument.
  +> <Arg2>
```

### Loose vs Strict Mode

- **Loose** (default): `+` = support, `-` = attack
- **Strict**: `+` = entailment, `-` = contrariness, `><` = contradiction

Set via frontmatter:
```yaml
model:
  mode: strict
```

## Premise-Conclusion Structures (PCS)

PCS reconstructs an argument's internal logic with numbered steps:

### Basic PCS

```argdown
<Simple Argument>

(1) All humans are mortal.
(2) Socrates is human.
----
(3) Socrates is mortal.
```

- **Premises**: Numbered items `(1)`, `(2)`, etc. before the inference
- **Inference line**: `----` (4 or more hyphens)
- **Conclusion**: Numbered item after the inference line

### Multi-step Arguments

```argdown
<Complex Argument>

(1) First premise.
(2) Second premise.
----
(3) First intermediary conclusion.
(4) Third premise.
(5) Fourth premise.
----
(6) Final conclusion.
```

### Expanded Inferences (with rules or metadata)

```argdown
<Detailed Argument>

(1) All humans are mortal.
(2) Socrates is human.
--
Modus Ponens {uses: [1,2]}
--
(3) Socrates is mortal.
(4) Mortal beings are impermanent.
--
{uses: [3,4]}
--
(5) Socrates is impermanent.
```

- Expanded inferences start and end with `--` (2+ hyphens)
- Content between the `--` lines can be inference rule names or YAML data
- `{uses: [1,2]}` specifies which premises are used

### Titled Statements in PCS

```argdown
<Argument A>

(1) [Premise One]: The first premise.
(2) [Premise Two]: The second premise.
----
(3) [Main Conclusion]: The conclusion follows.
```

Using titled statements connects the PCS to the broader argument map.

### Relations on PCS Statements

```argdown
<Main Argument>

(1) [P1]: Evidence shows X.
    +> <Supporting Arg>
    <- <Counter Arg>
(2) X implies Y.
----
(3) [Conclusion]: Therefore Y.
    +> [Further Claim]
```

## Headings

Markdown-style headings structure the document and create **groups** in the argument map:

```argdown
# Main Topic

## Subtopic A

[Statement A]: Something about topic A.

## Subtopic B

<Argument B>: Something about topic B.

### Sub-subtopic

[Detail]: A more specific point.
```

- Use `#`, `##`, `###`, etc.
- Headings create sections → sections become groups (grey boxes) in the map
- **Statement group assignment**: first occurrence in the document determines the group
- **Argument group assignment**: the definition location determines the group

## Tags

Categorize elements with hashtags:

```argdown
<Argument>: Description. #deism #best-explanation #inductive

[Statement]: Position text. #ethics #core-claim

// Bracketed tags for tags with spaces or punctuation
[Another]: Text. #(my complex tag!)
```

- Hyphenated tags: `#tag-name`
- Bracketed tags: `#(tag with spaces)`
- Tags can be used for: filtering/selection, colorization, categorization

## Metadata / Data Flags

Add YAML metadata to elements using `{}`:

### Inline format

```argdown
[Statement]: Text. {isInMap: true, color: "#ff0000"}
<Argument>: Text. {source: "Smith 2020"}
```

### Block format

```argdown
[Nietzsche's Slogan]: God is dead. {
  sources:
    - "Nietzsche, Thus Spoke Zarathustra"
    - "Nietzsche, The Gay Science"
}
```

### Special data flags

| Flag | Purpose |
|------|---------|
| `{isInMap: true}` | Force-include element in the map |
| `{isInMap: false}` | Force-exclude element from the map |
| `{color: "#hex"}` | Set element's color |
| `{uses: [1,2]}` | In PCS: specify which premises an inference uses |

## Frontmatter Configuration

YAML configuration at the document start between `===` markers:

```argdown
===
title: My Argument Analysis
author: John Doe
date: 2024-01-15
selection:
  statementSelectionMode: all
model:
  mode: strict
map:
  argumentLabelMode: title
dot:
  graphVizSettings:
    rankdir: TB
color:
  colorScheme: colorbrewer-set3
===

[Main Thesis]: The central claim.
```

See `configuration-reference.md` for all available settings.

## Comments

```argdown
// Single-line comment (C-style)

/* Multi-line
   comment (C-style) */

<!-- HTML-style
     comment -->
```

Comments are completely ignored by the parser.

## Bold and Italic Text

```argdown
[Statement]: This has *italic* and **bold** formatting.

// Also with underscores:
[Another]: This has _italic_ and __bold__ formatting.
```

## Links

Markdown-style links in statements:

```argdown
[Statement]: See [Wikipedia](https://en.wikipedia.org) for details.

// Internal links (to headings, statements, or arguments)
[Reference]: See [Main Topic](#main-topic) for context.
```

## Shortcodes (Unicode Symbols & Emojis)

Shortcodes are surrounded by dots `.` or colons `:`:

```argdown
[s1]: q :love: (p .->. q)
  + <a1>: :+1: :happy:
```

### Logical Symbols

| Shortcode | Unicode | Meaning |
|-----------|---------|---------|
| `.~.` / `:~:` | ¬ | Negation |
| `.A.` / `:A:` | ∀ | Universal quantifier |
| `.E.` / `:E:` | ∃ | Existential quantifier |
| `.->` / `:->:` | → | Implication |
| `.<->` / `:<->:` | ↔ | Biconditional |
| `.v.` / `:v:` | ∨ | Disjunction (OR) |
| `.^.` / `:^:` | ∧ | Conjunction (AND) |

### Emojis

| Shortcode | Emoji |
|-----------|-------|
| `:love:` | ❤️ |
| `:+1:` | 👍 |
| `:-1:` | 👎 |
| `:happy:` | 😊 |
| `:sad:` | 😢 |
| `:think:` | 🤔 |
| `:scream:` | 😱 |
| `:eye-roll:` | 🙄 |

### ArgVu Font

The [ArgVu font](https://github.com/christianvoigt/argdown/tree/master/packages/ArgVu) provides ligatures that display shortcodes as their unicode counterparts without changing the underlying code. Enable `dlig` font ligatures to use.
