# Positioning, study design, and analyses

This file covers deciding what the work claims, planning how to test it, and running the tests. The aim is a claim stated at exactly the strength the literature and the evidence allow, tested by analyses that could have come out the other way.

Scale this to the request. "Is my idea novel?" is a positioning study answered in chat. "How would I test this?" is a design answered with a short plan. A paper needs all of it, written down in `plan/PLAN.md` and `results/RESULTS.md`.

## Positioning an idea

Write the user's idea as a candidate claim, first in their words and then as a precise, falsifiable statement. Add alternatives when the user started from a broad direction, or when their claim comes back unsupported. For a quick check, suggest alternatives in a sentence. For a paper, or when the user asks, draw them from a gap study and from the open questions in reviews.

Test each candidate against the literature (`literature.md`, "Testing a claim"), with a small number of conversations each and the candidates in parallel. Then run the candidate-claim loop on the precise statement (`agent-bayes.md`). Each candidate comes out confirmed, qualified, or unsupported, and is placed in the field by what it builds on, what it answers, and what it contrasts with, all cited.

**Novelty.** A claim is novel relative to the corpus only if no prior statement of it was found. A novelty verdict always includes a search outside the corpus (`corpus.md`). State its scope (where you searched, with which queries), and say "no prior statement found in …" rather than "novel".

## Reshaping the question

Positioning may show that the question itself should change. It may already be answered, ill-posed, too broad for the evidence, or framed better another way in the literature. Propose a reshaped question with the reason and the evidence (citation keys, study paths). How the change is adopted depends on how the user works:

- **If they handed the work over,** adopt the better question, and tell them in the next report.
- **Otherwise,** present the current and proposed questions side by side, with your recommendation, and wait for their choice.

Either way, update `QUESTION.md` and log the old question, the new one, the reason, and the evidence.

Once analyses have been planned and run on a question, changing the question or the central claim goes back to the user in any case. That includes narrowing, reversing, or withdrawing the claim because of results. Present the evidence and your recommendation. When a claim's predictions fail, propose dropping it or inverting it into a finding, never a softened version that dodges the result. If the question narrows after results exist, record it in the History of `QUESTION.md`, and say in the paper's limitations that the narrowing came after the results.

## How the field tests claims like this

Before designing, ask the literature how papers in this corpus test claims like these:

- the data, tasks, baselines, and metrics they use;
- their sample sizes and statistical procedures;
- the threats to validity they are criticized for.

This is the standard of evidence the work will be judged by. Match it or beat it, and justify any departure.

## Designing the test

Break each claim into hypotheses narrow enough for a single test. Give competing explanations their own hypotheses, so the tests can tell them apart. For each hypothesis, specify in advance:

- **the route.** It can be an experiment (new data, a simulation, or a re-analysis of existing data) or research. Research means a test against the literature, a secondary analysis of published results, or a formal argument.
- **the prediction:** its direction and rough magnitude.
- **the decision rule,** with three outcomes: supported, refuted, and an inconclusive zone between them. Fixing the rule first is what makes a surprise legible as a surprise instead of something to explain away.
- **the analyses** that feed it: for each, its purpose and sample size, whether it is primary or a sensitivity check, and which rule it feeds.

The research routes need their own specifications:

- **A test against the literature** needs its evidence protocol fixed in advance: the queries, the inclusion rule, and what counts as disconfirming evidence.
- **A formal argument** needs its assumptions stated, and what would count as a counterexample.

Then list the threats to validity and how each is handled. Estimate the cost (compute, credits, money, time), and check it against the budget.

## Detectability: can the design answer the question?

A design that cannot detect the effect in question can never refute the null, and an absence claim then passes by default. Check what the design can resolve before the main analyses run. The check is essential for any claim of absence or equivalence, such as "no effect", "X does not differ from Y", or "synchronous". For other claims, size the check to the stakes.

1. **Simulate.** Generate data under the planned design, with a known true effect at several sizes including zero. Keep everything else as planned: the sample structure, measurement errors, model, and processing. Repeat each setting enough times to estimate how often the decision rule reaches each outcome.
2. **State the detection criterion** in advance. For example: "P(D > 0) ≥ 0.95", or "the 95% interval excludes 0".
3. **Report** the smallest effect detected with useful probability (for example 80%), and what the rule returns when the true effect is zero.
4. **Decide.** The question may need effects smaller than the design can detect. Then it cannot be answered with the planned data, and the user must hear it. The options are to reshape the question, gather more data, or proceed with a descriptive framing that says so plainly.

Small calibration pilots to set parameters may run before the check. They go to `results/pilot/`, and pilot data never enters `RESULTS.md` or `numbers.json`. Disclose them, and never let a pilot on the same data shape the decision rules silently.

## PLAN.md

In a project, write the design down before the main analyses run:

```
# Plan
## Claims                 id · statement · positioning (builds on · answers · contrasts with, cited) · novelty scope
## What would answer each claim
## Detectability          simulation · criterion · smallest detectable effect · verdict (answerable | limited | unanswerable)
## Hypotheses and decision rules
## Analyses               id · purpose · n · primary or sensitivity · feeds rule
## Threats to validity
## Cost estimate
## Pre-specification      date · pilots run before writing, and on what data
## Added analyses         appended later, see "No side doors"
## History                earlier claim and design versions, with what changed them
```

When the user is guiding, or asked to see the design first, present the claims, the detectability verdict, and the decision rules, and wait. Otherwise proceed and log it. Once the main analyses start, the decision rules are frozen. A real redesign is a new plan version, and the results that depended on the old one are redone.

## Running analyses

**No side doors.** Every analysis that runs is in the plan.

- **An analysis added later,** at the request of a reviewer, the user, or a surprising result, is first appended to the plan. Give its purpose, its sample size or number of runs, its detection criterion, and whether it could change a verdict. A check of power, sensitivity, or robustness states in advance what result would count as a problem.
- **Deviations** after runs start are logged with what changed and why. Examples: extending trials, changing an estimator, re-measuring with a better parser.

**Surface, don't adopt.** Two things go to the user before they reach the results:

- a result that would overturn a pre-specified verdict, such as a sensitivity run that turns "supported" into "refuted";
- a change in which analysis counts as primary.

Present the evidence, the alternatives, and your recommendation. Meanwhile, continue on your recommended path, marked provisional (SKILL.md, "Work with the user").

**Research tests** run exactly as specified:

- **A test against the literature** looks as hard for disconfirming evidence as for support: contradicting results, failed replications, boundary conditions. It records every source considered and its verdict.
- **A secondary analysis** is scripted and reproducible, with the citation key and page for every number taken from a paper. Extract tabular data from papers through page views into `results/data/*.csv`, with the document id and printed page on every row. Make a second, independent extraction pass and reconcile the differences before analysing. Supplementary data files and data repositories are datasets, not paper text, so read them directly and record their provenance.
- **A formal argument** is written in full and checked step by step. A gap in it makes the verdict inconclusive, not supported.

**Harness rules** for experiments and simulations:

- **Make it incremental and resumable.** Append results as trials complete, keyed by (arm, trial), and skip completed keys on a rerun.
- **Make it fault-tolerant.** A failed trial drops that one trial, and the drop is recorded.
- **Make it deterministic where possible.** Record seeds. Note when a tool seeds deterministically, so that repeated runs are not mistaken for independent evidence.
- **Measure against fixed ground.** Freeze task sets before measuring, use reference implementations for ground truth, and guard backtests against lookahead.
- **Track costs.** Record tokens, compute, time, and money per arm, and report cumulative spend against the budget.
- **Track long runs.** Run them in the background, poll cheaply, and log what is in flight and how to check it before a session ends.
- **Record provenance.** Note the source, version, and license of each dataset.

**Honest analysis:**

- Give intervals and sample sizes for every estimate (Wilson intervals suit proportions), and convergence diagnostics for every model reported, not only the ones you criticize.
- Watch for estimator bias. Watch for parse or format failures counted as capability failures, so measure format compliance separately. Watch for conditioning errors, such as counting steps after a failure. Watch for variation between items hidden under an average, and report per-item rates when they vary.
- When a result surprises you, test the structural explanation first (is the surprising direction even possible?). Then extend the trials, and only then narrate.
- Treat negative and partial results with the same care as confirmations. Report dropped trials, never hide them.

## Results

Generate every figure and table with a script into `results/figures/`, so they regenerate when the data changes. Have the same scripts write every number the paper will report to `results/numbers.json`, as `{"key": value}` with stable, readable keys (`d1_median`, `h1_p_later`). Store each value as it should appear in print: rounded, with units or its interval where needed, for example `"h1_effect": "0.41 [0.30, 0.53]"`. The paper inserts these values by placeholder, verbatim, never by hand.

`results/RESULTS.md` groups the predictions by hypothesis. For each prediction, give:

- the route;
- the outcome: the measurement with n and intervals, or the evidence for and against, with citation keys;
- the verdict under its pre-specified rule: supported, refuted, or inconclusive, with its bounds or what would resolve it;
- the figures and tables that show it;
- any deviation or added analysis that touches it.

Close with a verdict per claim, and with unexpected observations stated as observations, not claims. When a verdict calls for changing a claim, that goes to the user ("Reshaping the question" above).

When the plan changes, rerun only the analyses the change touches. The harness keys make this cheap.
