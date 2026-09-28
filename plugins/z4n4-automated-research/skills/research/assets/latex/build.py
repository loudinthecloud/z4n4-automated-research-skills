r"""Convert {slug}/paper/paper.md to paper.tex with the research skill's LaTeX template.

Expects, next to this script (in {slug}/paper/latex/):
  preamble.tex  - template with @@TITLE@@, @@AUTHOR@@, @@ABSTRACT@@ placeholders
  refs.json     - {"title": ..., "author": <raw LaTeX byline>,
                   "citations": {"<display string>": "<metadata slug>"},
                   "manual": {"<display string>": "<full reference text>"},   (optional; overrides full_reference)
                   "cite_pages": false}                                       (optional; default true)
And in the slug root: paper/paper.md, corpus/metadata.json.
A stamp frontmatter block at the top of paper.md (older projects) is stripped before conversion.

Citations render as the paper's own author-year-page text; the reference list is built verbatim from each
cited work's `full_reference` in metadata.json (or the manual entry), one entry per display string.

Markdown conventions handled:
  ## / ###                          -> \section* / \subsection*
  ## Abstract                       -> abstract block in the preamble (dropped when the paper has none)
  ([Display: pages](cite:<uuid>))   -> (Display: pages)
  ([Display](ref:manual))           -> (Display), for software, data, or curves listed under "manual"
  - item / 1. item (nested)         -> itemize / enumerate
  **bold**, *italic*, `code`        -> \textbf, \emph, \texttt
  "Table N. caption" + pipe table   -> captioned longtable with repeating header, caption kept as written
  "Listing N. caption" + code fence -> framed captioned listing float
  ![alt](path) + "*Figure N. cap*"  -> captioned figure float
  bare code fence                   -> unbreakable verbatim minipage
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
md = (ROOT / 'paper' / 'paper.md').read_text().replace('\r\n', '\n')
if md.startswith('---\n'):
    md = md.split('\n---\n', 1)[1] if '\n---\n' in md else ''
cfg = json.loads((HERE / 'refs.json').read_text())
meta = json.loads((ROOT / 'corpus' / 'metadata.json').read_text())
CITES, MANUAL, PAGES = cfg.get('citations', {}), cfg.get('manual', {}), cfg.get('cite_pages', True)

CITE = re.compile(r'\[([^\]]+?): ([^\]]+?)\]\(cite:[0-9a-f-]{36}\)')
REF = re.compile(r'\[([^\]]+?)\]\(ref:manual\)')
LIST = re.compile(r'^(\s*)(- |\d+\. )(.*)$')
SYMBOLS = {'¹⁴': r'\textsuperscript{14}', '²': r'\textsuperscript{2}', '⁰': r'\textsuperscript{0}',
           '⁴': r'\textsuperscript{4}', '∝': r'$\propto$'}
USED = {}
MISSING = set()


def reference(disp):
    if disp in MANUAL:
        return MANUAL[disp]
    if disp not in CITES or CITES[disp] not in meta:
        MISSING.add(disp)
        return ''
    m = meta[CITES[disp]]
    if m.get('full_reference'):
        return m['full_reference']
    return f"{', '.join(m.get('authors', []))}. {m.get('year', '')}. {m.get('title', '')}. {m.get('venue', '')}."


def cite_text(m):
    disp, pages = m.group(1).strip(), m.group(2).strip()
    if disp not in USED:
        USED[disp] = reference(disp)
    return f'{disp}: {pages}' if PAGES else disp


def esc(t):
    t = t.replace('\\', r'\textbackslash{}')
    for a, b in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'), ('_', r'\_'),
                 ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}'), ('{', r'\{'), ('}', r'\}')]:
        t = t.replace(a, b)
    for a, b in SYMBOLS.items():
        t = t.replace(a, b)
    return re.sub(r'"([^"\n]+)"', r"``\1''", t)


def ref_text(m):
    disp = m.group(1).strip()
    if disp not in MANUAL:
        MISSING.add(disp)
    elif disp not in USED:
        USED[disp] = MANUAL[disp]
    return disp


def inline(t):
    t = CITE.sub(cite_text, t)
    t = REF.sub(ref_text, t)
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f'\x00{len(codes) - 1}\x00'
    t = esc(re.sub(r'`([^`]+)`', keep, t))
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\emph{\1}', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: r'\texttt{' + esc(codes[int(m.group(1))]) + '}', t)


def caption(line, kind):
    num, rest = line.split('.', 1)
    return f'\\caption*{{\\small\\textbf{{{num}.}} {inline(rest.strip())}}}'


def table(rows, cap):
    n = len(rows[0])
    first = 0.24 if n > 3 else 0.4
    other = (0.98 - first) / (n - 1) if n > 1 else 0
    col = '>{\\raggedright\\arraybackslash}p{%.3f\\textwidth}'
    spec = col % (first - 0.012) + ''.join(col % (other - 0.012) for _ in range(n - 1))
    head = ' & '.join('\\textbf{' + inline(c) + '}' for c in rows[0]) + ' \\\\'
    t = ['{\\footnotesize', '\\setlength{\\tabcolsep}{3pt}', f'\\begin{{longtable}}{{{spec}}}']
    if cap:
        t.append(caption(cap, 'Table') + '\\\\')
    label = cap.split('.', 1)[0] + ' (continued)' if cap else '(continued)'
    t += ['\\hline', head, '\\hline', '\\endfirsthead',
          f'\\multicolumn{{{n}}}{{l}}{{\\small\\textit{{{label}}}}}\\\\', '\\hline', head, '\\hline', '\\endhead']
    for r in rows[1:]:
        r = (r + [''] * n)[:n]
        t.append(' & '.join(inline(c) for c in r) + ' \\\\')
    return t + ['\\hline', '\\end{longtable}', '}']


body_md = md.split('\n## References')[0]
lines = body_md.split('\n')
out, i, in_code = [], 0, False
pending_caption = pending_listing = open_listing = None
stack = []


def open_list(kind):
    out.append('\\begin{itemize}[leftmargin=*,itemsep=1pt,topsep=2pt]' if kind == 'ul'
               else '\\begin{enumerate}[leftmargin=*,itemsep=1pt,topsep=2pt]')


def close_lists(depth=-1):
    while stack and stack[-1][0] > depth:
        out.append('\\end{itemize}' if stack.pop()[1] == 'ul' else '\\end{enumerate}')


while i < len(lines):
    ln = lines[i]
    if in_code:
        if ln.startswith('```'):
            if open_listing:
                out += ['\\end{verbatim}\\end{framed}', caption(open_listing, 'Listing'), '\\end{listing}']
                open_listing = None
            else:
                out.append('\\end{verbatim}\\end{minipage}\\par\\medskip')
            in_code = False
        else:
            out.append(ln)
        i += 1
        continue
    m = LIST.match(ln)
    if m and not ln.lstrip().startswith('|'):
        depth, kind = len(m.group(1)), 'ul' if m.group(2) == '- ' else 'ol'
        close_lists(depth)
        if not stack or stack[-1][0] < depth:
            stack.append((depth, kind))
            open_list(kind)
        elif stack[-1][1] != kind:
            close_lists(depth - 1)
            stack.append((depth, kind))
            open_list(kind)
        out.append('\\item ' + inline(m.group(3)))
        i += 1
        continue
    if stack:
        if ln.strip() and ln.startswith('  '):
            out.append(inline(ln.strip()))
            i += 1
            continue
        if not ln.strip():
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and (LIST.match(lines[j]) or lines[j].startswith('  ')):
                i += 1
                continue
        close_lists()
    if re.match(r'^Table (\d+|[A-Z]\d+)\. ', ln):
        pending_caption = ln
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        continue
    if re.match(r'^Listing \d+\. ', ln):
        pending_listing = ln
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        continue
    if ln.startswith('!['):
        path = pathlib.Path(re.match(r'!\[[^\]]*\]\(([^)]+)\)', ln).group(1)).name
        cap = ''
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].startswith('*Figure'):
            cap = caption(lines[j].strip().strip('*'), 'Figure')
            i = j
        out += ['\\begin{figure}[H]', '\\centering', f'\\includegraphics[width=0.9\\textwidth]{{{path}}}', cap,
                '\\end{figure}']
        i += 1
        continue
    if ln.startswith('```'):
        if pending_listing:
            open_listing, pending_listing = pending_listing, None
            out += ['\\begin{listing}[H]', '\\begin{framed}\\begin{verbatim}']
        else:
            out.append('\\par\\medskip\\noindent\\begin{minipage}{\\textwidth}\\begin{verbatim}')
        in_code = True
        i += 1
        continue
    if ln.startswith('# '):  # the title; the byline after it comes from refs.json
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and not lines[i].startswith('#'):
            i += 1
        continue
    if ln.startswith('## Abstract'):
        out.append('ABSTRACT_START')
    elif ln.startswith('## '):
        out.append(f'\\section*{{{inline(ln[3:])}}}')
    elif ln.startswith('### '):
        out.append(f'\\subsection*{{{inline(ln[4:])}}}')
    elif ln.startswith('|'):
        tbl = []
        while i < len(lines) and lines[i].startswith('|'):
            tbl.append(lines[i])
            i += 1
        rows = [[c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', r.strip()[1:-1])] for r in tbl]
        out += table([r for r in rows if not all(set(c) <= set('-: ') for c in r)], pending_caption)
        pending_caption = None
        continue
    else:
        out.append(inline(ln))
    i += 1
close_lists()

if MISSING:
    raise SystemExit('citations missing from refs.json or metadata.json: ' + '; '.join(sorted(MISSING)))

body = '\n'.join(out)
abstract, rest = '', body
if 'ABSTRACT_START\n' in body:
    _, rest = body.split('ABSTRACT_START\n', 1)
    first_section = rest.find('\\section*{')
    first_section = len(rest) if first_section < 0 else first_section
    abstract, rest = rest[:first_section].strip(), rest[first_section:]

refs = ['\\section*{References}', '\\begin{list}{}{\\leftmargin=1.5em\\itemindent=-1.5em\\itemsep=3pt}']
refs += ['\\item ' + inline(r) for _, r in sorted(USED.items(), key=lambda kv: kv[0].lower())]
refs.append('\\end{list}')

preamble = (HERE / 'preamble.tex').read_text()
preamble = preamble.replace('@@TITLE@@', inline(cfg['title'])).replace('@@AUTHOR@@', cfg['author'])
if abstract:
    preamble = preamble.replace('@@ABSTRACT@@', abstract)
else:  # an essay or note without an abstract
    preamble = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}\n?', '', preamble, flags=re.S)
(HERE / 'paper.tex').write_text(preamble + '\n' + rest + '\n\n' + '\n'.join(refs) + '\n\n\\end{document}\n')
print(f'paper.tex written, {len(USED)} references')
