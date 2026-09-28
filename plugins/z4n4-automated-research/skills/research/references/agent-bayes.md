# Agent Bayes

Agent Bayes is the only source of literature claims and citations. The rest of this skill decides _what_ to ask. This file says _how_ to ask it, and how far to trust the answer.

## Terminology

Talk to the user in Agent Bayes's product words. The MCP tools use internal names, and those identifiers must be passed through unchanged:

| Say to the user             | In the MCP tools and the project files                   |
| --------------------------- | ------------------------------------------------------- |
| library                     | knowledge base: `kb_*` tools, `kb_id`, the `kb:` fields |
| passage                     | chunk: `chunk_id` (the citation key)                    |
| search, "search by meaning" | `rag_search_project`, `rag_search_document`             |
| library chat                | project chat: `project_chat_*` tools                    |

## Session start

Call `get_instructions` first in every session, again after an MCP reconnect, and whenever you are unsure of a rule. It is server-enforced: the server also asks for it again after an idle gap and after a run of tool calls, so the rules survive follow-ups and context compaction. When a tool fails with `instructions_not_fetched`, call `get_instructions` and retry the same call. It carries the live prices, the model list and recommendations, the entitlements and limits for this account (open-upload cap, libraries per project, parallel chats), and the citation rules. If it contradicts this file, the server wins.

## State location

Inside a research slug, Agent Bayes state lives in `{slug}/ab/`. Quick tasks outside a slug keep no state files: they report ids and spend in chat. Files:

- `state.md`: the project id, the attached library ids (which one is primary), and document ids with titles and `file_id`s.
- `credits.md`: one line per spending operation: date, task, operation, estimate, actual (from `credits_summary`).

Record every id the moment it is created and reuse ids on resume. Library chat conversation ids go in the transcript of the work that asked, next to the answer.

## Research-integrity rules

1. **Never invent a literature claim** (SKILL.md, integrity rule 1). Your own reasoning appears only as clearly authorial framing, uncited.
2. **Keep each citation with the claim it backs.** When compressing or restating, never merge citations, drop them, or move them between claims.
3. **Unverified keys never reach the user or a file.** Run the verification procedure below first.
4. **Numbers must match the source.** A quantitative claim is valid only if the resolved passage, or the page itself when the number sits in a table or figure, contains the number. A real key next to a garbled number is a failure.
5. **Preserve qualifications.** A foil, assumption, or limitation a paper reports is not that paper's conclusion. A one-source result is not field consensus. When you cite a paper's figures, give its own reading of them too if it differs from yours: a paper's table cited for a position its authors reject misrepresents it.
6. **Absence is provisional.** A just-indexed paper may not be searchable yet. Re-query before concluding the library lacks something.
7. **Read papers through Agent Bayes, never from a local PDF's text.** Never extract a paper's content locally (`pdftotext`, PyMuPDF text, OCR, or opening the PDF with a file-reading tool) for claims, quotes, numbers, or metadata. A PDF's text layer is often broken: garbled OCR, columns interleaved, reading order scrambled, tables flattened, footnotes spliced into sentences. Use search for passages, library chat for claims, and page views for tables and figures. A paper that is not indexed yet gets indexed, not read locally. Local PDFs exist only to be uploaded, and local tools may touch them only for file checks and page counts. The one exception is a confidential manuscript under review that the user declines to upload (`review.md`).

## Projects and libraries

A project is the retrieval scope: it attaches libraries (`kb_attach`), and search and library chat read every library attached to it. Use one project per research slug. For a quick task outside a slug, reuse an existing project whose attached libraries are exactly the ones the task needs (`project_list` shows `attached_kb_ids`). If there is none, use a single project named `z4n4-scratch` (create it once): `kb_detach` every library the task does not need, and attach only the libraries that clearly cover the question, so retrieval reads nothing else. Whether to create a library or reuse one is a corpus decision (`corpus.md`). Attaching counts against the account's libraries-per-project limit.

## Indexing mechanics

What to index and the cost gate are in `corpus.md`. This is _how_ to index:

1. `document_upload_begin`, then PUT the file **from disk** with curl, sending the returned Content-Type exactly. Then call `document_index_pdf(kb_id, upload_id=...)` with a per-paper `idempotency_key`.
2. Work in batches no larger than the open-upload cap from `get_instructions`. Index a batch, then start the next.
3. **Metadata.** Omit title, authors, year, and full_reference, and the index tool reads them off the PDF for free. Pass fields only when you have them from an exact-id lookup (arXiv id, DOI), never from a search snippet. If `metadata_source` comes back `llm`, or the title looks like a journal name, look at the first page (below) and fix the record with `document_update`.
4. **Retries and duplicates.** A retry with the same `idempotency_key` replays instead of charging twice. `deduplicated: true` means the library already holds the file, and nothing was charged. `conflict` means an earlier copy's indexing ended CANCELLED or FAILED: remove the dead file with `document_file_delete`, then index again with the same `upload_id`.
5. Record each document id and `file_id` in `state.md` as it is created, so a resumed run skips papers that are already indexed.
6. **Readiness.** Poll `document_list` for the whole library (per-file status in one call), not per document. Before any study, every paper the question needs must read COMPLETED. A queued paper silently yields thin answers.

## Search (flat fee per call)

`rag_search_project` (every library attached to the project) and `rag_search_document` (one paper) return citation-ready passages: `chunk_id`, page ranges, and the full reference.

- **Batch query variants.** Each call takes 1–10 queries, runs them concurrently, and costs the same small flat fee (rate in `get_instructions`) whatever the query count. Phrase a subject three to six ways in one call: it covers far more ground at the same cost. A call with one query wastes most of what you paid for.
- **Narrow** with `source_filter` (author, year, title, or reference text) and `include_tags`.
- **Figures** come back as passages starting "AI Generated Visual Description of <label>:" and are cited like any other passage.
- Use search to scout, locate sources, check exact wording, and score coverage. Passages can be appendix noise, so draw conclusions, comparisons, and positions from library chat.

## Look at pages (free)

`document_view_pages` renders up to 4 pages of an indexed file, for tables, figures, maps, and plates the passage text cannot convey. Address the file with a search passage's `source.document_id` and `content_id`, and pass pages as `page_range` with `numbering="pdf"` or as `actual_page_range` with `numbering="printed"`. Each image fills your context, so locate the page with search first.

## Library chat (where claims are generated)

`project_chat_message` asks the project chat agent a question. It retrieves from every attached library, reads the passages in context, and answers with tight, citation-backed claims. It spends credits.

1. Send the message with an `idempotency_key` that is unique to this message: end it with a random part, for example a few hex characters from `uuidgen`, never only a topic and a date. Reuse a key only to retry the very same message after a failure. A response with `"replayed": true` returns an answer stored earlier, not a new run, so if you meant to ask something new, send it again with a fresh key. Omit `conversation_id` to start a conversation, or pass one to continue it. The call returns `conversation_id` and `answer_id` immediately.
2. Poll `project_chat_status`, passing `answer_id` and the returned `next_cursor` as `message_cursor`, until the answer is complete. Its `credits_summary` then gives the actual cost. A focused answer usually takes under a minute, and a deep-work answer a few minutes. Between polls, wait in whatever way your environment allows. Judge elapsed time from the clock (for example `date`) or the message timestamps, never from the number of polls, because some waits return at once. A run that is still streaming is working: never start a second run of the same question because one seems slow. Report a duration only when you measured it.
3. Save the answer verbatim, citations included, with its `conversation_id`, to the transcript of the work that asked for it, **before doing anything else with it**. In a quick task with no project folder, keep it in context and still verify its keys. `project_chat_read` recovers a stored conversation.

Guidelines:

- **Parallelism is conversations.** Each conversation runs one answer at a time, and a project runs a few conversations in parallel (the account limit is in `get_instructions`). Send independent questions as separate new conversations at once and poll them together. If the server refuses another concurrent run, wait for one to finish.
- **Follow-ups** that build on an answer continue its conversation (same `conversation_id`). A new conversation knows nothing of the others, so restate the prior findings it needs in the prompt.
- **Model and effort.** For extraction, focused questions, and any answer the user wants short, use the cheapest model `get_instructions` recommends, at the default `reasoning_effort` and `research_depth="auto"`, even when the question is about positions or debates. For substantial work (a review's positions and debates, critical synthesis, deriving aspects, drafting prose), use the **deep-work settings**: a mid-range model from the `get_instructions` list with `reasoning_effort="high"` and `research_depth="deep"`. Effort and depth matter more here than the most capable model. Move to a more capable model only when a deep-work answer is still unsatisfying. When `get_instructions` warns that a model adds details the passages do not state, prefer another model where claim fidelity matters, and verify its specifics.
- **Scope** a question to tagged documents with `include_tags` when the work concerns a subset.
- **Work with the agent, don't script it.** Treat the research agent as a knowledgeable colleague, not a form to fill. Ask real questions in natural language and let it choose how to search, what to read, and how to organize its answer. Leave room for it to reframe the question, disagree with a premise, point to papers you did not name, or surface something unexpected. Those answers are often the most valuable ones, and a rigid template suppresses them. When an answer goes somewhere useful that you did not anticipate, follow it up conversationally rather than steering back to the script.
- **What a prompt should convey**, only as much as the task needs. Include the user's question in their words, the scope and the size, any terms or papers your preliminary search surfaced, any output shape that genuinely matters to the task, and that substantive claims should carry their citation keys. Never add framing from your own background knowledge (SKILL.md, "Understand the request"). For substantial critical work, also ask it to be critical and specific and to say where evidence is thin or contested. The prompts quoted in these references are illustrations of intent, not templates to copy word for word. Adapt them to the question, the corpus, and what earlier answers revealed.

Mindmaps (`mindmap_*`, `agent_message`) are Agent Bayes's other way of working, in which the agent builds a tree of cited claims as the output. This skill writes its own outputs and uses library chat. Use a mindmap only when the user asks for one.

## Candidate-claim loop

When you believe something the library has not said, never write it as a finding. Send it to library chat as a candidate: state the claim and ask for confirmation, refutation, or qualification with citations. There are three outcomes:

- **Confirmed:** use the agent's phrasing and keys.
- **Qualified:** use the qualified version.
- **Unsupported:** the claim survives only as explicit authorial framing, uncited, or not at all.

## Citation verification (mandatory before keys reach the user or a file)

1. Collect every citation key in the draft. `ref:manual` citations (software, data, calibration curves) carry no key and are checked by exact-id lookup instead.
2. Resolve them all with `rag_resolve_chunks`, in batches of up to 50. Require zero stale ids and every requested id present. A key that is neither returned nor reported stale is malformed, usually a key prefix spliced onto another id's tail. To fix it, search the document (`rag_search_document`) for the claim's content and replace the key.
3. For every quantitative claim, read the resolved passage and confirm the numbers match. When the number comes from a table or figure the passage only describes, look at the page. On a mismatch, discard the claim and re-derive it from the source, or re-ask with the passage in view.
4. The displayed page range must equal the passage's `actual_page_range` (fallback `page_range`).

Citation format everywhere: `([Author et al. Year: pages](cite:<chunk_id>))`, with short display text and the key verbatim and in full. Library chat sometimes writes a key as `cite:<label> | <chunk_id>`. Keep only the chunk id, verbatim: `(cite:<chunk_id>)`. Bibliographic data comes only from `full_reference` fields or `corpus/metadata.json`, never from memory. A reference list is built from these strings verbatim.

## Credits

Search costs a small flat fee per call, whatever the number of queries in it, so batch them. Page views, listings, `rag_resolve_chunks`, and metadata detection are free. Indexing is priced per page and is usually the dominant cost. Read both per-page rates from `get_instructions`, never from memory or this file: the estimate (the expected charge) and the reserve (held when indexing starts, then settled to actual). Library chat likewise reserves an estimate and settles to actual usage, usually far below the reserve. Check `credits_balance` before spending: the balance must cover the reserve, not only the estimate. Split an indexing batch the balance cannot cover. In a project, log every spending operation in `credits.md`, with searches as one line per session giving the call count. Before an operation or a batch of chats whose estimate would take cumulative spend past what the user agreed to (`cost_budget` in QUESTION.md, or what the task plainly implies), ask. Report cumulative spend in LOG.md at milestones.

## Reconcile on resume

1. Confirm the ids in `state.md` still resolve (`project_get`, `kb_get`).
2. Call `document_list` and compare it with the recorded documents. Fold documents indexed outside this skill (for example through the Agent Bayes app or Zotero) into `corpus/CORPUS.md` and `corpus/metadata.json`.
3. For each conversation the log records as in flight, check `project_chat_status`, and save each finished answer to its transcript.
