# Reviewing a paper

A review answers two questions. Does the paper answer its question? Does it hold up to the standard of its field and venue? Everything else serves those two.

Scale it to the request. "Check the citations" is the citation check alone. "Is this ready?" or "referee this" is the full review.

## Which review

- **A paper this project wrote.** The question, the venue, and the length budget come from `QUESTION.md`. You fix what the review finds, as below.
- **The user's own draft from elsewhere.** The user's question and venue stand in for `QUESTION.md`. Without them, use the paper's own stated question and its venue. Report what you find. Edit the draft only if the user asks for a revision.
- **Refereeing someone else's paper** for a journal or a conference. You write a referee report in the venue's usual form:
  - a summary of the paper and its contribution;
  - major concerns;
  - minor concerns;
  - a recommendation.

  You make no fixes and run no second cycle. Keep the tone respectful and specific, and make every concern actionable.

**Reading the paper under review.** Read a Markdown, LaTeX, or Word source directly. When refereeing, assume the manuscript is confidential unless the user says otherwise, because many venues forbid uploading it to third-party or AI services. Ask before uploading it anywhere. If the user agrees, or the paper is not confidential, a PDF is read through Agent Bayes like any other paper: index it, after telling the user the small cost, then use search and page views. If the user declines, read the PDF locally, page images first and its text layer only with care. Check its citations by exact-id lookup only. This exception covers the paper under review, never the sources it cites. For the judge, prepare a faithful Markdown rendering built from the indexed passages and page views, or use the user's source file if they have one.

**The venue's norms.** When the venue is named, read its author guidelines on the web. If the library holds papers from that venue, or the project has `literature/FIELD_NOTES.md`, use them as the norm. Otherwise write a short norms note first (`literature.md`, "Field notes").

## Checking citations

- **Papers with Agent Bayes keys.** Resolve every key, and check each quantitative literature claim against its passage (`agent-bayes.md`, citation verification).
- **Papers with ordinary citations** ("Smith 2020"). First check that every reference exists and that its metadata is right, by exact-id lookup (free, `corpus.md`). Then check whether each source supports the claim it is cited for. The right corpus for that is the cited works themselves. Those already in one of the user's libraries need no indexing, so attach that library. Estimate the cost of indexing the rest, and index them if the user agrees. Then check each claim with search and the candidate-claim loop. If the user declines the cost, check the load-bearing claims against an existing library instead. Say in the report what was checked and how.

## Your own passes

- **Consistency.** Numbers agree across the abstract, body, tables, and figures. Figure and table references match. Terms are stable. Flag any mention of how the paper was produced.
- **Overreach and hedging.** Look for these problems:
  - claims stronger than their evidence;
  - one-source claims posing as consensus;
  - "first", "only", or "never" that a single counterexample would kill;
  - hedging in the wrong direction, either too much or too little.

  For a project paper, compare each claim's strength with its verdict in `results/RESULTS.md`.
- **Method.** Check that intervals and n are present, that dropped trials are reported, and that deviations and added analyses are disclosed. For any claim of absence, ask whether the design could have detected the effect. Ask what a referee would raise that the limitations leave out.
- **Missed related work.** Search the library for indexed works that bear on the key claims but are not cited. Look outside it for the rest (`corpus.md`). For a project paper, related work that matters enters the paper only after it is indexed and verified.

## The judge

Spawn one reviewer sub-agent with fresh context. Give it the paper, the question with what would answer it, the target, the venue, and the length budget. Give it the field or venue notes too, if they exist. Give it nothing else from the project. Ask it to answer, in order:

1. Does the paper answer the question? Yes, partly, or no, with reasons.
2. Does it read as a normal article in this venue? Consider length, prose, structure, synthesis, and the use of figures and tables.
3. Which three to five changes matter most, ranked?
4. Is the methodology sound?
5. What grade does it get out of 10? The gate is 9.0 unless the user set another.

Rigour comments are welcome after these. Save the report in `paper/review/`. If sub-agents are unavailable, do a second, deliberately adversarial read yourself, and say so in the verdict. For a referee report, the judge's answers are one input to your report, not a substitute for it.

**The web reader.** When Perplexity is connected, send the paper to it in parallel with the judge. The judge sees only the paper. The web reader checks the paper against the wider literature, which catches what a paper-only read cannot. Use `perplexity_reason` with `search_context_size: "high"`. Give it the paper, the question with what would answer it, and the venue, and nothing else from the project. Ask it for:

1. work that bears on the key claims but is not cited, especially work that contradicts, refines, or already answers them;
2. claims that the wider literature contests or has moved past;
3. objections the field raises against this kind of method or design;
4. the three to five changes that matter most, ranked.

If the paper is too long for one message, send the abstract, introduction, related work, discussion, and conclusion, because these carry the claims it checks. Skip it silently when Perplexity is absent. A confidential manuscript goes to it only with the user's consent (see "Reading the paper under review"). Save its answer in `paper/review/` beside the judge's report. It gives no grade, because the gate stays with the judge. Treat the works it names as leads. Check that each exists by exact-id lookup (`corpus.md`). For a project paper, a work enters the paper only after it is indexed and verified. Run it once, in the first cycle. In the second cycle the judge checks the fixes. For a referee report, it is one more input, like the judge.

**Triage every suggestion** from the judge and the web reader, the ranked ones included:

| Category              | Action                                        |
| --------------------- | --------------------------------------------- |
| in scope, necessary   | fix                                           |
| nice to have          | list in the verdict, do not fix               |
| out of scope          | record with one line of why, and drop         |

A suggestion is in scope only if it serves answering the question at the venue's standard. A judge always produces suggestions, and it favors additions over cuts. Accept a suggestion only if it names a real defect you can verify. Fixes keep the paper within its length budget, so an addition is paid for with a cut, or goes to the user. A fix that needs a new analysis is added to the plan first (`studies.md`, "No side doors"). A fix that would change the question or the central claim goes to the user.

**The second cycle.** After the fixes, send the judge the new paper and a change log listing each triaged item and what was done. Continue the same judge's conversation if you can. Otherwise spawn a fresh judge and give it the previous report as well. It answers the same five questions again. There is no third cycle. If the paper is still below the gate after two cycles, take the verdict to the user rather than looping.

## Before the verdict

For a project paper, re-verify the final text:

- every citation key resolves, and the displayed pages equal the passage pages;
- every result number came from a placeholder, and `results/numbers.json` is current;
- nothing the fixes added is an unchecked claim. Diff the reviewed and final versions, and verify every new literature claim or number.

## The verdict

Write `paper/review/VERDICT.md`, or give it in chat for a quick review. It contains:

- the judge's answers and grade for each cycle, and whether the paper passed the gate;
- the web reader's main points, if it ran;
- whether the paper answers its question at the venue's standard: yes, partly, or no;
- the fixes made, the nice-to-have suggestions not taken, and the out-of-scope ones dropped;
- the remaining weaknesses, each with what would address it: wording, the claim, the evidence, more literature, or the method.

Present it to the user. Whether to revise further or change course is their decision. When the user disputes a weakness, record their reasoning, and drop the weakness if their case holds.
