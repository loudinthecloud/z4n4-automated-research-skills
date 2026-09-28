# Writing

Write like an author from the field. When the project has `literature/FIELD_NOTES.md`, it records how the field's papers are structured, how long they run, how they argue and hedge, and how many figures and tables they carry. Match it. These rules hold for any length, from a related-work paragraph or an essay to a full paper. The outline, assembly, and typesetting machinery matter once there is a paper.

## Prose, not lists

A paper is continuous prose that synthesizes. Each paragraph makes one point and weaves evidence, interpretation, and citations into an argument. Never turn an argument into bullet points or a sequence of labelled fragments ("*X.* … *Y.* …"): a list of findings is not a synthesis. Use a list only for a true enumeration the reader will scan, such as exclusion sets, sample lists, or hypotheses, and then keep it short. Tables carry dense numbers; the prose says what they mean.

## Invisible production

The paper never discusses its own production. It does not mention corpus size, the retrieval agent, a count of indexed papers, or the process, and it uses the field's own terms rather than tool vocabulary. Spend those words on what the research provides.

Treat reviewer feedback, the user's comments, and earlier drafts as instructions, and write each section straight into its final form. Never mention rejected framings, discarded approaches, or objections raised along the way. This hides how the paper was written, never what the research found. Deviations from the plan, analyses added after it, a question narrowed after the results, and the limitations all stay in. So do inverted findings when the results call for them.

## The outline: the paper as an argument

Before drafting a paper, write `paper/OUTLINE.md`:

- **The thesis:** the paper's answer to the question in `QUESTION.md`, at the strength the results allow.
- **The sections,** in the order the field uses. For each section, give the part of the answer it carries, the evidence it uses, and its word budget. The budgets sum to `length_budget`, or to the field's norm from the field notes.
- **The figures and tables:** which ones, what each shows, and how many, within the field's usual count.

Only claims the evidence supports appear as findings, at the strength their verdict allows. Inverted findings appear when the results call for them.

Structure follows the field and the paper type. When an empirical paper has no clear convention, start from this order: abstract, introduction, related work, theory or model, methods and experiments, discussion with limitations, conclusion, references. Survey, theory, position, and humanities papers are organized differently.

Show the user the outline before drafting, unless they handed the work over. The outline is where a paper's direction is set, and it is far cheaper to change than a draft.

## Drafting

**The one fixed order: introduction and abstract last.** Write the body first, in any order, then the introduction, then the abstract. They frame what the paper actually shows, so they need the rest to exist.

Write each section to its own file in `paper/sections/`. The file's numeric prefix fixes the reading order, not the writing order (`01-abstract.md`, `02-introduction.md`, …). The abstract comes first, under the heading `## Abstract`.

**Who writes what:**

- **Related work and other literature-facing prose** are drafted in Agent Bayes library chat with the deep-work settings. Give it the length, a coverage list, the order, the rule "every substantive claim carries its citation link", and the rules from "Writing for the reader" through "Punctuation" below. Feed it an existing review's concept matrix and positions rather than re-deriving the field. Relay the draft with its citations intact, then verify the keys.
- **Theory, methods, results, and discussion** are yours. Each embedded literature claim either reuses a verified Agent Bayes claim or passes the candidate-claim loop first.
- **Your own result numbers are never typed.** Write `{{num:<key>}}`, and the assembly script inserts the value from `results/numbers.json`. A number that is not there yet goes back to the analysis, not into the text.
- **Limitations** are yours. State them honestly, including deviations and analyses added after the plan.

**Assemble** with `python3 <skill>/scripts/assemble.py .` from the project folder. It builds `paper/paper.md` from `QUESTION.md` (title, authors) and the sections, fills the number placeholders, and reports the word count against `length_budget` and the share of list lines. Fix what it reports. When a section runs long, cut it rather than letting the paper grow. Never hand-edit `paper.md`: fix the section and reassemble.

**Revising.** To revise one section, edit it, re-verify its keys and numbers, and reassemble. When upstream work changes (the question, the plan, the results), rewrite only the sections carrying the affected claims and numbers. When the user edits a section by hand, keep the edit, verify any new literature claim, and never regenerate over it.

## Writing for the reader

Before drafting a section, picture its reader and situation: an author from the field, a specialist checking the method, a researcher from a neighbouring field skimming for the result. Readers build understanding one sentence at a time, so order the text to arrive at the paper's claim. Test each sentence with "would this reader nod or squint?".

- **Make reading cheap.** Prefer simple constructions over clever ones, and short sentences over stacked clauses.
- **Be specific.** Concrete beats complete: name the works, systems, datasets, numbers, and the exact conditions under which results hold. Authority comes from specificity, and the introduction and methods must show command of the field.
- **Introduce names before relying on them.** A system, method, or dataset that is not common knowledge gets a short introduction with its citation at first mention, saying what it is and what it does. A clause is often enough: "X, a retrieval benchmark of 2,000 legal questions, shows …". After that, use the name. Gloss well-known domain terms at first use only when the paper should also reach neighbouring fields.
- **Keep one term per concept.** Never vary a term for elegance, because a synonym suggests a different thing.
- **Restate distant context.** Readers forget definitions, hypotheses, and key numbers from pages earlier. Restate one briefly where a section relies on it more than a page or two later.
- **A little life is welcome** within the field's register: a vivid example, a well-chosen verb, a question that sets up a section. Do not overdo it, and never trade a simple construction for it.

## Leading and weaving

Lead each section, and usually each paragraph, with one succinct, precise sentence that carries its point, then support it. The reader gets the point at once, chooses how deep to read, and places each detail in the frame the lead built. If the lead needs context to be understood, give that context first, briefly. Whenever you introduce a method, a definition, or an analysis, state what it is for before its mechanics. A result leads with the finding.

The rest weaves context, claims, and interpretation in whatever order the reader needs next.

- Build a piece of context once and let a batch of claims follow.
- Interpret only when it tells the reader something the claim does not.
- Avoid a long preamble whose purpose the reader cannot yet see, and a claim whose context is missing, which the reader can only stall on or take on faith.

## Hedging and sources

Calibrate hedging per claim rather than spraying it. State a replicated benchmark number flat, attribute a single-paper result ("X report"), and name the competing readings of a contested point. Authorial framing (the hypothesis, interpretations, predictions) is uncited by design and marked as yours ("we read this as"). Never hedge your own verified measurements, and never present a one-source claim as field consensus.

Represent sources faithfully. Keep each source's qualifications. A foil or assumption that a paper reports is not that paper's conclusion. Cite results to the papers that introduced them, not to later surveys that retell them. Where the field has since moved, say how, and present recent results and consensus as what they are, not as proof.

## Punctuation

No em-dashes and no semicolons, except the "; " between citations inside parentheses. Split the sentence instead. A comma never joins two full sentences.

## Markdown conventions

Write in the shape the LaTeX converter expects, so typesetting needs no rework:

- **Title block:** the assembly script opens the paper with the title as a `#` heading and a line of authors and affiliations, both from the frontmatter of `QUESTION.md`. Section files therefore never use `#`.
- **Headings:** `##` for sections, `###` for subsections.
- **Tables:** a paragraph line `Table N. <caption>` directly before the pipe table.
- **Listings** (code or specifications): a line `Listing N. <caption>` directly before a fenced code block that should be a boxed float.
- **Figures:** an image line, then an italic `*Figure N. <caption>*` line stating what is plotted and with what intervals.
- **Numbering:** the converter keeps your N exactly as written. Number tables, listings, and figures each in order of appearance, caption every one, and reference each from the prose. Never start a prose paragraph with "Table N" or "Listing N", which the converter reads as a caption.
- **Citations:** always `([Display Year: pages](cite:<chunk-uuid>))`, with one display string per work and the pages always present. Disambiguate works with the same author and year by suffix (2010a, 2010b), since each display string maps to one reference. Software, datasets, calibration curves, and other works that back no literature claim are cited as `([Display Year](ref:manual))`, with a `manual` entry in `refs.json`. Typesetting maps each distinct string to one entry of `corpus/metadata.json`, and that entry's `full_reference` goes into the reference list verbatim.
- **What the converter cannot do:** it has no math mode, so write symbols in Unicode or words rather than `$…$`. Bullets use `- `, never `*`. Figure file names must be unique, because figures are found by file name.
- **Essays and notes** without an abstract typeset fine: leave out `## Abstract`, and the abstract block is dropped.

## Typesetting

Typesetting needs `xelatex`. If it is missing, ask the user once whether to install a LaTeX toolchain. If they decline, `paper/paper.md` is the final output. Then add a last section file, `99-references.md`, under `## References`: one entry per display string, copied verbatim from `full_reference` or the `manual` text, sorted by display string. Reassemble.

1. **Copy the template.** On first use, copy `<skill>/assets/latex/preamble.tex` and `<skill>/assets/latex/build.py` into `paper/latex/`. From then on, the project's copies are the source to adapt.
2. **Write `paper/latex/refs.json`.** It holds the title and a LaTeX byline from `QUESTION.md`, and `citations`, a map from every citation display string in `paper.md` to its slug in `corpus/metadata.json`. The reference list is built from each slug's `full_reference` verbatim. A work cited from outside the corpus gets an entry under `manual`, with its full reference. When the venue has its own reference style, put the formatted entry under `manual` for that display string, built from the fields in `corpus/metadata.json`; a `manual` entry wins over `full_reference`. When the venue cites without pages, set `"cite_pages": false`: the pages stay in the markdown for checking but are not printed.
3. **Copy the figures** the paper references into `paper/latex/`.
4. **Build.** Run `python3 build.py` in `paper/latex/`, then `xelatex paper.tex` twice. The build stops and names any citation display string missing from `refs.json`. Never hand-edit `paper.tex`: fix the section or `build.py`, then rebuild.
5. **Inspect every page** as an image, and grep the text layer. Check that:
   - captions are attached and numbered as in the prose;
   - tables fit, and continue across pages with their headers;
   - lists and emphasis render;
   - citations show pages;
   - the reference list is complete, with one entry per cited work;
   - no markdown syntax is left.

   Problems in content go back to the sections. Problems in conversion go to `build.py`.
