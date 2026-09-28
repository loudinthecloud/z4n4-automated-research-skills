# The corpus

The corpus is the set of papers indexed in an Agent Bayes library that the work reasons over. Every literature claim comes from it, so it decides what the work can say. Indexing mechanics are in `agent-bayes.md`. This file covers what to index and how to get it.

## Reuse before you build

List the user's libraries (`kb_list`) before searching anywhere else. A library that covers the topic can simply be attached to the project (propose it first when the user is guiding). That is free, and re-indexing the same papers is not. Several projects may share one library. When you attach one, record its id in `ab/state.md` and as `kb:` in `QUESTION.md` and `corpus/CORPUS.md`. Then build `corpus/metadata.json` from each document's `full_reference`, enriched by exact-id lookup where an arXiv id or DOI is present.

## How big

There is no target count. The corpus is big enough when the question is covered: each claim the work will make, and each aspect it leans on, is backed by enough independent primary sources to state it at the intended strength. Start with the core papers, not an exhaustive sweep. When later work hits the library's limits, note the papers still to find in the log and come back here. Examples of limits: a thin aspect, a claim the library cannot support, a gap, related work a reviewer would expect. Growth stops when the question is covered, not when a number is reached.

For a quick task (one review, one question), a small focused corpus is right. For a paper, plan searches from the question and the aspects you draft from it, which later become the coverage table (below).

## Finding papers

Use the instrument that best answers the need at hand:

1. **The user's Agent Bayes libraries**, first. `rag_search_project` also tells you whether a paper is already indexed.
2. **Perplexity, when it is connected**, for broad and recent sweeps (`perplexity_search` with recency filters, one query per aspect plus variants). Skip it silently when it is absent, because the free instruments below cover the same ground.
3. **Scholarly APIs:**
   - **arXiv.** Fetch metadata by id with `https://export.arxiv.org/api/query?id_list=<id1>,<id2>`, and search with `search_query=all:<terms>&max_results=50`, adding `sortBy=submittedDate` for recency. PDFs are at `https://arxiv.org/pdf/<id>`. Keep to about one request every 3 seconds.
   - **OpenAlex.** Search with `https://api.openalex.org/works?search=<terms>&per-page=50`, look up a DOI with `/works/doi:<doi>`, and filter for recency with `filter=from_publication_date:<YYYY-MM-DD>`. Lookup by exact id beats title search, which mismatches freely.
   - **Semantic Scholar.** Search with `https://api.semanticscholar.org/graph/v1/paper/search?query=<terms>&fields=title,authors,year,venue,externalIds,abstract,openAccessPdf`. It is useful for open-access links and for papers outside arXiv. Back off on HTTP 429.
4. **Web search**, to find a paper you can already name, a project page, a dataset, or code.
5. **A browser tool**, for pages search tools cannot reach: JavaScript-heavy sites, HTML-only papers, supplementary material. When its session carries the user's own logins, it can retrieve paywalled papers through their subscriptions (see Acquiring papers).

**Snowballing.** Once a core set exists, follow references backward (OpenAlex `referenced_works`) and citations forward (`filter=cites:<W-id>`) from the most central papers. This is where the best missing papers usually come from.

**Screening.** Record each candidate in `corpus/candidates.md` as screened in or out, with one line of why. Log queries and their yield in `corpus/search-log.md`. For a small task, a short list in the log is enough.

**Source quality.** Prefer primary research that passed peer review. When a preprint has a published version, index the published one. Use a preprint when no reviewed version exists, and say so. Surveys help map a field, but the claims the work rests on should trace back to the primary papers.

**Freshness.** Recency is one consideration among several:

- **Founding papers often matter most.** When a claim rests on an original result, index the original, not only the surveys that retell it.
- **Newer is not more correct, and consensus is not proof.** Report consensus as consensus, and keep well-argued dissent in view.
- **When the field may have moved** on a claim that carries the work, run a recency sweep for work that refines, contradicts, or replicates it. Report what it finds, and let the user choose what to index.

**Looking outside the corpus.** Sometimes you only need to know whether work exists outside the library: is a gap real, did the paper miss related work? Search with the instruments above without indexing anything, and report what you found. Absence in a search is evidence, not proof.

## Metadata

Never trust titles or authors from snippets or from memory. Fetch metadata by exact id (arXiv `id_list`, OpenAlex, DOI). For a paper with neither, let the index tool detect the metadata from the PDF and copy the detected fields. Write `corpus/metadata.json`, keyed by a stable paper slug: title, authors, year, venue, arxiv/doi, abstract, and `full_reference`. The reference list is built from `full_reference` verbatim, so its accuracy matters.

## Acquiring papers

arXiv and open-access PDFs download freely. Check that the first bytes are `%PDF`. Local PDFs exist only for upload and page counts, never for reading (integrity rule 7 in `agent-bayes.md`).

**PDFs the user provides** are indexed as given. Do not screen them, check their source, or swap in another version. Files the user supplies are the user's responsibility. Mark them `user-provided` in `candidates.md`.

**Paywalled papers.** Never scrape around a paywall and never use shadow libraries. If a browser session carries the user's institutional access, retrieve the paper through it with their permission. The user logs in themselves, and you never enter credentials. Otherwise tell the user what you need (title, venue, DOI, why it matters), note it in the log, and continue with other papers.

## Cost and indexing

Count pages locally (`pdfinfo` or PyMuPDF) and price them with the rates in `agent-bayes.md` ("Credits"). Show the user the papers and the estimate first when the batch goes beyond what they agreed to, or when they asked to see the papers (SKILL.md, "Work with the user"). Outliers, such as a 300-page thesis, are their call. Then index following `agent-bayes.md`.

## CORPUS.md and the coverage table

`corpus/CORPUS.md` is the corpus at a glance:

- frontmatter with `kb: <library id>`;
- one line per document that has finished indexing (paper slug, AB document id, title, year, pages);
- for a paper-scale project, the coverage table and a short profile (size, years spanned, dominant and least covered aspects, outliers).

Rewrite it after each indexing batch, and whenever the library changed outside this skill (the Agent Bayes app, Zotero).

**The coverage table** shows which source treats which aspect of the question, and how deeply. It is derived from `corpus/coverage.json`, the single editable source, whose schema is documented in `<skill>/scripts/render_matrix.py`.

1. **Aspects.** Derive 6–15 aspects from the question and the corpus: the themes, problems, methods, and findings the papers deal with. Probe candidates with batched searches, ask library chat what else the corpus addresses around them, and split or merge until each is distinct. Check that every paper is covered by some aspect or noted as an outlier.
2. **Score** each cell in half steps: 0 absent, 1 mentioned, 2 substantive (a section, experiment, or result), 3 central. Score from search hits, batching each aspect's phrasings in one call. Hits in the abstract or results count for more than mentions in related work. Confirm contested cells with library chat. Store each cell's best passage keys as `evidence`, and set `confirmed` once library chat has confirmed it. Papers that no aspect covers usually mean an aspect is missing.
3. **Render** with `python3 <skill>/scripts/render_matrix.py corpus/coverage.json --thin 2`.
4. **Thin aspects.** An aspect the question depends on, with fewer than two sources scoring 2 or more, is thin. Grow the corpus there or say why not.

The user may rename, merge, or split aspects, or override cells (marked `"manual": true`). Keep their changes on a rerun, and re-score only new documents or changed aspects. `render_matrix.py --pairs 10` lists aspect pairs rarely treated together, which is useful when looking for gaps.
