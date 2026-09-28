# Studying the literature

Three kinds of study come up again and again: reviewing a topic, answering one question in depth, and finding what the literature leaves open. They mix freely. A review often raises a question worth studying in depth, and a gap study needs a review's map. Every Agent Bayes call follows `agent-bayes.md`.

Scale the study to the request. A question asked in conversation ("what does the field say about X?") follows the quick-question recipe in SKILL.md. A review for a paper needs the full protocol below. Ask yourself what the answer will be used for, and stop when it serves that.

## What a study delivers

Whatever its kind, the answer has the same shape:

- **The bottom line** comes first, stated at exactly the strength the evidence allows.
- **The argument** follows, in paragraphs that synthesize concept by concept or debate by debate, never paper by paper. Each substantive claim carries its verified citation.
- **A positions table** comes next when there are positions to compare: question, position, proponents, evidence, challenged by, and status (consensus, contested, or open).
- **What the literature does not settle**, and the scope of the study: the corpus boundary, the inclusion rule, and the date.

In a chat answer, the bottom line, the cited argument in prose paragraphs, and one line of scope and spend are enough. Lists are for true enumerations, never a substitute for argument, and bold-led bullets are still a list. In a project, save studies under `literature/` (for example `reviews/<topic>/REVIEW.md`, `questions/<question>/ANSWER.md`, `gaps/<seed>/GAPS.md`), with each study's raw library chat answers in its own `transcripts/` folder (for example `literature/reviews/<topic>/transcripts/`).

## Reviewing a topic

**Choose the review type first.** It decides the protocol, the synthesis, and the output. Snyder (2019) distinguishes broad approaches, and Grant & Booth (2009) catalogue finer types.

| Type                        | Purpose                                                              | Synthesis                                    | Use when                                             |
| --------------------------- | -------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| **Integrative / critical**  | critique and synthesize perspectives to frame or position an argument | conceptual: frameworks, positions, tensions  | positioning a contribution; related work (default)   |
| **Scoping**                 | map the extent and nature of a body of work                          | charting what exists, where, by which method | the field is diffuse and the first need is a map     |
| **Semi-systematic**         | trace how a topic developed across research traditions               | thematic and chronological streams           | the topic spans disciplines or has shifted over time |
| **Systematic**              | answer a narrow question by comparing all eligible evidence          | tabulated effect directions and sizes        | the question is specific and the studies comparable  |

**The protocol.** For a substantial review, write it at the top of the review before sweeping:

- the scope (aspects from the coverage table, or the question);
- the inclusion rule, with what was excluded and why;
- the queries per aspect and sub-concept;
- what to extract from each source: claim, method, setting, key numbers, and stated limitations;
- how evidence strength will be appraised;
- the synthesis modes, chosen from the list below.

**Sweep with search first, because it is cheap.** Break each aspect into 3–8 sub-concepts, using the terms the corpus itself uses rather than your own knowledge of the field, and batch their phrasings in `rag_search_project` calls. Read the passages and fill a **concept matrix** (after Webster & Watson 2002) in the review's `matrix.md` (`literature/reviews/<topic>/matrix.md`). Its rows are sources and its columns are sub-concepts, and each cell holds a short extraction with its chunk key. Organizing by concept is what keeps the synthesis from becoming "A said, B said".

**Positions and debates.** For each aspect, ask library chat with the deep-work settings what positions exist. For each position, ask for its proponents, the type of evidence, the strongest objection and who raises it, and whether the question is consensus, contested, or open. Run the aspects in parallel. Consensus describes where the field stands, not what is true. Keep well-argued dissent visible, and trace positions back to the founding papers. When a contested point matters to the question and one answer leaves it unresolved, study it in depth (below).

**Appraise.** Tag each substantive claim with its evidence strength: replicated, single study, theoretical, or opinion. Look for methodological differences that explain contradictions, since different measurements of the same construct often do.

**Synthesize.** Choose the modes that fit:

- by concept;
- by positions and debates;
- by chronology and research streams;
- by methodological comparison;
- in evidence tables, for a systematic review.

Calibrate hedges to the appraisal. State a replicated result flat, and attribute a single study to its authors ("X report"). When the user wants review prose, such as related work, draft it in library chat with the deep-work settings. Feed it the matrix and the positions, and relay the result with its citations intact.

## One question in depth

Use this for a question that matters: a contested point, a claim to test, or the question the user asked. First sharpen the question into something answerable, and note the sharpening. Choose how many conversations to spend. About six is typical, but use fewer for a narrow question. Check the estimated credits against the budget.

1. **Plan.** Decompose the question into sub-questions: definitions, the evidence on each side, mechanisms, boundary conditions, and differences in measurement. Fill them from the user's question and from what scouting searches show the corpus contains, not from your own knowledge of the field. Scout each one with batched search to see that the corpus has material on it.
2. **First wave.** Send each sub-question as its own new conversation, in parallel, on the cheapest recommended model. Ask for citations, and for thin or contested evidence to be flagged. Save every answer verbatim as it completes.
3. **Follow-ups.** Spend the remaining conversations where they change the answer:
   - go deeper in a conversation;
   - reconcile answers that conflict;
   - test your emerging answer with the candidate-claim loop;
   - ask for the evidence that cuts against it.

   Stop at saturation, when two runs add nothing new.
4. **Synthesis.** Run one deep-work conversation that restates the findings. Ask for the answer, its strength, the conditions under which it holds, the dissent, and what the corpus cannot tell.
5. **Verify** every key, and write the answer in the shape above. If the corpus does not cover something that matters, note what to find.

**Testing a claim against the literature** is the same study, scaled as described at the top of this file, and aimed at four questions:

- what the corpus establishes that the claim builds on, and by whom exactly;
- whether the corpus already makes the claim, fully or in part, and where;
- what contradicts or complicates it;
- what it leaves open that the claim would fill.

## What the literature leaves open

Start from a seed: a direction in the user's words, or the whole corpus. Run these steps:

1. **Coverage limits.** Look for empty or thin cells on the seed's aspects in the coverage table. Look for aspect pairs rarely treated together (`python3 <skill>/scripts/render_matrix.py corpus/coverage.json --pairs 10`). Search adjacent populations, settings, scales, and methods for sparse edges.
2. **What the papers say is open.** Search for stated limitations and future work. Then study in depth what the corpus identifies as unknown, unresolved, or contradictory about the seed.
3. **Classify each candidate gap**: stated as open, a contradiction, an intersection, a new context, a method, or a coverage gap.
4. **Look outside the corpus** for each candidate (`corpus.md`). Relevant work found there makes it a gap in the corpus, so note those papers to index. Nothing found makes it a candidate gap in the field.
5. **Turn real gaps into questions.** Raise a varied set of candidate questions. Test each for novelty, answerability (by experiment, analysis, proof, or synthesis), and significance. Include some bold candidates alongside the safe ones, and prefer questions whose answer would be interesting either way. Drop the answered, unanswerable, and trivial ones with one line of why each. Sharpen the survivors, and repeat until the shortlist is stable.

   For each shortlisted question, give the question, how it could be answered, why it matters (cited), the nearest existing work (cited), and how feasible it is.

## Field notes: how the field writes

When the work will become a paper, learn the field's habits from its own papers. The paper is drafted and judged against these notes. Write `literature/FIELD_NOTES.md` during the first substantial review, and refresh it when the corpus grows substantially or the venue changes.

1. **Pick 5–10 exemplars** from the corpus that are the kind of paper this project will write: the same field and genre, ideally the target venue or its peers. Venues are in `corpus/metadata.json`.
2. **Learn their norms** through search, page views, and one deep-work library chat question:
   - the usual structure and section order;
   - article length;
   - register: prose density, hedging, first person;
   - how many figures and tables there are, and what they show;
   - how methods and uncertainty are reported;
   - the citation style.
3. **Record the field's broad views** in a few cited sentences each: its main positions on the question, and what it treats as settled.

Keep the notes short and concrete, and tie each norm to the exemplars that show it. Where the exemplars disagree, say so. The notes describe habits, not rules to follow blindly.

## Keeping studies current

- **When the corpus grows,** re-sweep only the new sources, and say whether any position changed status.
- **When the user edits** a positions table, a gap, or a field note, the edit is authoritative. Verify any new citation, and synthesize around the edit.
- **When the question is sharpened,** add runs and a new synthesis. A different question is a new study.
