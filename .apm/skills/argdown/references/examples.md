# Argdown Examples

Complete, realistic argument map examples at various complexity levels.

## Contents

- [Example 1: Simple Pro/Con Debate](#example-1-simple-procon-debate)
- [Example 2: Complex Multi-Argument Analysis with PCS](#example-2-complex-multi-argument-analysis-with-pcs)
- [Example 3: Policy Analysis with Groups and Tags](#example-3-policy-analysis-with-groups-and-tags)
- [Example 4: Oldschool Inference Tree](#example-4-oldschool-inference-tree)
- [Example 5: Full-Featured Example](#example-5-full-featured-example)
- [Example 6: Text-to-Argdown Reconstruction](#example-6-text-to-argdown-reconstruction)
- [Example 7: Same-Rank and Concentrate](#example-7-same-rank-and-concentrate)
- [Example 8: Dark Theme Map](#example-8-dark-theme-map)
- [Upstream Examples (from argdown/argdown)](#upstream-examples-from-argdownargdown)

## Example 1: Simple Pro/Con Debate

A basic two-sided debate with support and attack relations.

```argdown
===
title: Should Universities Require Attendance?
color:
  tagColors:
    pro: "#4CAF50"
    con: "#F44336"
===

[Mandatory Attendance]: Universities should require
  class attendance for all courses.

## Arguments For

<Learning Outcomes>: Regular attendance correlates
  with better grades and deeper understanding. #pro
  +> [Mandatory Attendance]

<Accountability>: Students who pay tuition should
  be encouraged to use the resources they've paid for. #pro
  +> [Mandatory Attendance]

## Arguments Against

<Adult Autonomy>: University students are adults
  and should manage their own time. #con
  -> [Mandatory Attendance]

<Self-Directed Learning>: Some students learn more
  effectively through independent study. #con
  -> [Mandatory Attendance]

<Accessibility>: Strict attendance policies
  disadvantage students with disabilities, jobs,
  or caregiving responsibilities. #con
  -> [Mandatory Attendance]
```

## Example 2: Complex Multi-Argument Analysis with PCS

An argument with detailed premise-conclusion structures and interconnections.

```argdown
===
title: The Ethics of Artificial Intelligence
selection:
  statementSelectionMode: with-title
color:
  colorScheme: colorbrewer-set3
===

# Central Question

[AI Ethics Thesis]: The development of advanced AI
  systems requires binding ethical regulations.

# Arguments For Regulation

<Existential Risk Argument>: Unregulated AI
  development poses existential risks. #pro
  +> [AI Ethics Thesis]

<Existential Risk Argument>

(1) [Rapid Progress]: AI capabilities are advancing
    faster than our ability to understand their
    implications.
(2) [Unpredictable Behavior]: Advanced AI systems
    can exhibit unpredictable behaviors.
(3) If progress outpaces understanding AND behavior
    is unpredictable, then significant risks exist.
----
(4) [Significant Risks]: Significant risks exist
    in unregulated AI development.
(5) Significant risks demand regulatory frameworks.
----
(6) [AI Ethics Thesis]

<Bias Amplification>: AI systems can
  amplify existing societal biases at scale. #pro
  +> [AI Ethics Thesis]

<Bias Amplification>

(1) AI training data reflects historical biases.
(2) [Bias at Scale]: Biased AI decisions affect
    millions of people simultaneously.
----
(3) Unregulated AI risks mass discrimination.

# Arguments Against Regulation

<Innovation Stifling>: Premature regulation
  could hamper beneficial AI research. #con
  -> [AI Ethics Thesis]

<Innovation Stifling>

(1) [Innovation Need]: AI research produces
    life-saving medical and scientific breakthroughs.
(2) Regulation introduces compliance costs
    and delays.
----
(3) Over-regulation risks slowing critical progress.

<Technical Infeasibility>: Current understanding
  is insufficient to write effective AI regulations. #con
  -> [AI Ethics Thesis]
  _> <Existential Risk Argument>

// The infeasibility argument undercuts the risk argument's
// inference — if we can't regulate effectively, the
// conclusion that regulation helps doesn't follow.

# Cross-cutting

[Bias at Scale]
  +> <Existential Risk Argument>

[Innovation Need]
  <- <Bias Amplification>
```

## Example 3: Policy Analysis with Groups and Tags

A structured policy analysis using sections as groups and tags for categorization.

```argdown
===
title: Remote Work Policy Recommendation
selection:
  statementSelectionMode: with-title
  selectedTags:
    - economic
    - social
    - operational
  selectElementsWithoutTag: false
color:
  tagColors:
    economic: "#2196F3"
    social: "#9C27B0"
    operational: "#FF9800"
dot:
  graphVizSettings:
    rankdir: LR
  statement:
    minWidth: 3
===

# Economic Factors

[Cost Savings]: Remote work reduces office
  space costs by 30-50%. #economic

[Talent Retention]: Flexible work arrangements
  reduce employee turnover. #economic

<Reduced Overhead>: Companies save significantly
  on facilities, utilities, and supplies. #economic
  +> [Cost Savings]

<Competitive Hiring>: Remote options attract
  candidates from a wider geographic area. #economic
  +> [Talent Retention]

# Social Factors

[Work-Life Balance]: Employees report better
  work-life balance with remote flexibility. #social

[Isolation Risk]: Extended remote work can lead
  to social isolation and reduced belonging. #social

<Commute Elimination>: Removing commutes gives
  employees 5-10 hours per week back. #social
  +> [Work-Life Balance]

<Loneliness Concern>: Remote workers miss informal
  social interactions that build relationships. #social
  +> [Isolation Risk]

# Operational Factors

[Productivity Impact]: Studies show mixed results
  on remote work productivity. #operational

<Deep Work Benefit>: Fewer interruptions enable
  sustained focus on complex tasks. #operational
  +> [Productivity Impact]

<Coordination Cost>: Asynchronous communication
  introduces delays in decision-making. #operational
  -> [Productivity Impact]

# Connections

[Cost Savings]
  +> [Work-Life Balance]

[Isolation Risk]
  -> [Talent Retention]
```

## Example 4: Oldschool Inference Tree

Traditional argument map showing all statements and inferential steps as individual nodes.

```argdown
===
title: Inference Tree - Climate Action Argument
selection:
  statementSelectionMode: all
model:
  explodeArguments: true
map:
  argumentLabelMode: none
  statementLabelMode: text
dot:
  argument:
    shape: circle
    minWidth: 0.2
  statement:
    minWidth: 4
    fontSize: 10
  graphVizSettings:
    rankdir: TB
color:
  colorScheme: colorbrewer-set2
===

<Climate Action Argument>

(1) [CO2 Rising]: Global CO2 levels have increased
    40% since pre-industrial times.
(2) [Greenhouse Effect]: CO2 is a greenhouse gas
    that traps heat in the atmosphere.
--
Basic Physics {uses: [1,2]}
--
(3) [Warming Follows]: Global temperatures are
    rising due to human CO2 emissions.
(4) [Impact Evidence]: Rising temperatures cause
    sea level rise, extreme weather, and
    ecosystem disruption.
--
Empirical Evidence {uses: [3,4]}
--
(5) [Action Needed]: Immediate action is needed
    to reduce CO2 emissions.
(6) [Feasibility]: Renewable energy technology
    is now cost-competitive with fossil fuels.
--
Practical Reasoning {uses: [5,6]}
--
(7) [Conclusion]: Governments should mandate
    rapid transition to renewable energy.
```

## Example 5: Full-Featured Example

Demonstrates colors, groups, tags, metadata, multiple relation types, and custom configuration.

```argdown
===
title: Should Social Media Require Age Verification?
author: Policy Research Team
date: 2024-06-15
selection:
  statementSelectionMode: with-title
  excludeDisconnected: true
model:
  mode: loose
  removeTagsFromText: true
map:
  statementLabelMode: title
  argumentLabelMode: title
  addTags: false
color:
  tagColors:
    safety: "#E53935"
    privacy: "#1E88E5"
    freedom: "#43A047"
    tech: "#FB8C00"
dot:
  graphVizSettings:
    rankdir: BT
    size: "12,10"
  statement:
    minWidth: 3
    fontSize: 11
  argument:
    minWidth: 2.5
    fontSize: 11
===

# The Central Question

[Age Verification]: Social media platforms should
  implement mandatory age verification for all users.
  {isInMap: true}

# Child Safety

<Protecting Minors>: Children face unique harms
  from social media including cyberbullying, predatory
  behavior, and mental health impacts. #safety
  +> [Age Verification]

<Protecting Minors>

(1) [Child Vulnerability]: Children lack the cognitive
    development to manage social media risks.
    {source: "APA, 2023"}
(2) [Documented Harms]: Research documents increased
    anxiety, depression, and self-harm among young
    social media users. {source: "Surgeon General Report, 2023"}
----
(3) [Protection Needed]: Children need protection
    from social media harms.
(4) Age verification is an effective protection mechanism.
----
(5) [Age Verification]

<Parental Responsibility>: Parents, not platforms,
  should control children's internet access. #freedom
  -> <Protecting Minors>

# Privacy Concerns

<Surveillance Risk>: Age verification requires
  collecting sensitive personal data, creating
  surveillance infrastructure. #privacy
  -> [Age Verification]

<Data Breach Risk>: Centralized age verification
  databases become high-value targets for hackers. #privacy
  -> [Age Verification]
  +> <Surveillance Risk>

[Technical Alternative]: Privacy-preserving age
  estimation can verify age without storing
  personal data. #tech #privacy
  _> <Surveillance Risk>
  _> <Data Breach Risk>

# Freedom of Expression

<Free Speech Concern>: Age gates create barriers
  to information access and may chill speech. #freedom
  -> [Age Verification]

<Precedent Risk>: Once age verification infrastructure
  exists, governments may expand its use for
  censorship. #freedom #privacy
  -> [Age Verification]

[Documented Harms]
  <- <Free Speech Concern>

// The documented harms of unregulated access counter
// the free speech argument — harm prevention can
// justify proportionate restrictions.

# Technical Feasibility

<Implementation Challenge>: No current technology
  can reliably verify age without significant
  false positives/negatives. #tech
  -> [Age Verification]

<Circumvention>: Tech-savvy minors will find
  ways around any verification system. #tech
  _> <Protecting Minors>

[Technical Alternative]
  -> <Implementation Challenge>
```

## Example 6: Text-to-Argdown Reconstruction

Demonstrates converting a prose paragraph into structured Argdown. Start by extracting claims, then identify support/attack relations.

**Source text:** _"Electric cars are better for the environment because they produce zero tailpipe emissions. However, the production of batteries requires mining rare earth minerals, which causes significant environmental damage. Still, over the vehicle's lifetime, the net carbon footprint is lower than combustion engines."_

```argdown
===
title: Electric Vehicles and the Environment
color:
  tagColors:
    pro: "#4CAF50"
    con: "#F44336"
    rebuttal: "#2196F3"
map:
  statementLabelMode: title
===

[EV Better]: Electric cars are better for the environment.

<Zero Emissions>: EVs produce zero tailpipe emissions,
  eliminating a major source of urban air pollution. #pro
  +> [EV Better]

<Battery Mining>: Battery production requires mining
  rare earth minerals, causing significant environmental
  damage to mining regions. #con
  -> [EV Better]

<Lifecycle Analysis>: Over the vehicle's full lifetime,
  the net carbon footprint of an EV is lower than a
  combustion engine, even accounting for battery production. #rebuttal
  -> <Battery Mining>
  +> [EV Better]
```

**Render:** `uv run scripts/render.py ev-environment.argdown`

## Example 7: Same-Rank and Concentrate

Demonstrates `sameRank` to align competing alternatives, and `concentrate: true` to merge overlapping edges.

```argdown
===
title: Programming Language Choice
dot:
  sameRank:
    - statements: ["Use Python", "Use Rust", "Use Go"]
  graphVizSettings:
    rankdir: TB
    concentrate: true
map:
  statementLabelMode: title
===

[Choose Language]: We need to pick a backend language.

[Use Python]: Python is the best choice. #option
[Use Rust]: Rust is the best choice. #option
[Use Go]: Go is the best choice. #option

<Ease of Use>: Python has the gentlest learning curve. #pro
  +> [Use Python]

<Performance>: Rust provides memory safety without GC overhead. #pro
  +> [Use Rust]

<Concurrency>: Go's goroutines make concurrent code simple. #pro
  +> [Use Go]

<Slow Runtime>: Python is slow for CPU-bound tasks. #con
  -> [Use Python]

<Complexity>: Rust's borrow checker has a steep learning curve. #con
  -> [Use Rust]

<Limited Generics>: Go's type system is less expressive. #con
  -> [Use Go]

[Use Python]
  +> [Choose Language]
[Use Rust]
  +> [Choose Language]
[Use Go]
  +> [Choose Language]
```

**Render:** `uv run scripts/render.py language-choice.argdown`

## Example 8: Dark Theme Map

Same structure as Example 1, rendered with the dark theme for presentations or dark-mode documents.

```argdown
===
title: Remote Work — Dark Theme
color:
  tagColors:
    pro: "#66BB6A"
    con: "#EF5350"
    middle: "#FFA726"
map:
  statementLabelMode: title
===

[Remote Default]: Remote work should be the default mode.

<Productivity Gains>: Studies show fewer interruptions
  and more deep work time when working remotely. #pro
  +> [Remote Default]

<Cost Savings>: Both companies and employees save on
  office space, commuting, and related expenses. #pro
  +> [Remote Default]

<Collaboration Loss>: Spontaneous brainstorming and
  whiteboarding are harder to replicate remotely. #con
  -> [Remote Default]

<Isolation Risk>: Remote workers report higher rates
  of loneliness and disconnection from team culture. #con
  -> [Remote Default]

<Hybrid Compromise>: A hybrid model (2-3 office days)
  captures most benefits while mitigating downsides. #middle
  -> <Collaboration Loss>
  -> <Isolation Risk>
```

**Render with dark theme:** `uv run scripts/render.py remote-dark.argdown --theme dark`

## Upstream Examples (from argdown/argdown)

Full `.argdown` files mirrored from the official [argdown/argdown examples
directory](https://github.com/argdown/argdown/tree/main/examples). Use these
as reference for real-world debates, advanced frontmatter (grouping,
colorSchemes, `model.mode`), and longer-form reconstructions than the
hand-crafted snippets above.

| Example | Description |
|---|---|
| [argdown-primer.argdown](../assets/argdown-primer.argdown) | Official primer demonstrating the full basic syntax — statements, titles, tags, links, pros/cons, indentation. Start here when learning the language. |
| [Populism-Core-Argument-Argdown-Example.argdown](../assets/Populism-Core-Argument-Argdown-Example.argdown) | David Lanius' reconstruction of the core argument of right-wing populism (AfD 2017 platform). Large, real-world PCS reconstruction. |
| [greenspan-schefczyk_hardwrap.argdown](../assets/greenspan-schefczyk_hardwrap.argdown) | Schefczyk/Betz analysis of Alan Greenspan's arguments on the 2008 financial crisis. Demonstrates `group.regroup`, `dot.graphVizSettings`, and `tagColors` by index. |
| [legalisation-softdrugs.argdown](../assets/legalisation-softdrugs.argdown) | Simple pros-and-cons adaptation (Sather 1999) on soft drug legalisation. Minimal frontmatter, clean pro/con tag pattern. |
| [semmelweis_betz.argdown](../assets/semmelweis_betz.argdown) | Stylized reconstruction of Semmelweis' childbed-fever debate. Uses `model.mode: strict` and three competing hypotheses (H1/H2/H3). |
| [state-censorship.argdown](../assets/state-censorship.argdown) | Detailed pros-and-cons reconstruction of state censorship (used as the "first example" in the online Argdown Guide). Uses `removeTagsFromText`. |

**Render any example:** `uv run scripts/render.py ../assets/<filename>.argdown`
