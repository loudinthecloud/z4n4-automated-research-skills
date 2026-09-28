#!/usr/bin/env python3
"""Assemble {slug}/paper/paper.md from QUESTION.md and paper/sections/*.md, and check its form (stdlib only).

QUESTION.md frontmatter (or paper/BRIEF.md in an older project) supplies the title block and the length budget:
    title: <paper title>
    authors:
      - Jane Doe (MIT)
    length_budget: 8000 words

Sections are concatenated in filename order (01-abstract.md, 02-introduction.md, ...); any stamp frontmatter (older projects)
on a section is dropped. Result numbers are written as {{num:<key>}} and filled from results/numbers.json;
an unknown key fails the assembly.

Form checks (reported; --strict turns them into failures):
    length   words over length_budget by more than --tolerance (default 0.10)
    lists    list-item lines over --max-list-share of prose lines (default 0.10)

Usage: assemble.py . [--strict] [--tolerance 0.1] [--max-list-share 0.1]   (run from the slug dir)
"""
import argparse
import json
import pathlib
import re
import sys

PLACEHOLDER = re.compile(r'\{\{num:([A-Za-z0-9_.\-]+)\}\}')
LIST_ITEM = re.compile(r'^\s*(?:[-*+] |\d+\. )')


def split(text):
    text = text.replace('\r\n', '\n')
    if text.startswith('---\n') and '\n---\n' in text[3:]:
        head, body = text[4:].split('\n---\n', 1)
        return head.split('\n'), body
    return [], text


def frontmatter(path):
    fm, key = {}, None
    for line in split(path.read_text())[0]:
        if line.startswith('  - ') and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(line[4:].split('  #')[0].strip())
        elif ':' in line and not line.startswith(' '):
            key, val = (s.strip() for s in line.split(':', 1))
            val = val.split('  #')[0].strip()
            fm[key] = val if val else []
    return fm


def fill_numbers(text, slug):
    keys = PLACEHOLDER.findall(text)
    if not keys:
        return text
    path = slug / 'results' / 'numbers.json'
    numbers = json.loads(path.read_text()) if path.exists() else {}
    missing = sorted({k for k in keys if k not in numbers})
    if missing:
        sys.exit(f'unknown number keys (not in results/numbers.json): {", ".join(missing)}')
    return PLACEHOLDER.sub(lambda m: str(numbers[m.group(1)]), text)


def words(text):
    return len(re.sub(r'\(cite:[^)]*\)', '', text).split())


def list_share(text):
    lines = [l for l in text.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '!', '*Figure', '```'))]
    return sum(bool(LIST_ITEM.match(l)) for l in lines) / len(lines) if lines else 0.0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('slug', nargs='?', default='.')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--tolerance', type=float, default=0.10)
    ap.add_argument('--max-list-share', type=float, default=0.10)
    a = ap.parse_args(argv[1:])
    slug = pathlib.Path(a.slug).resolve()
    fm = {}
    for anchor in (slug / 'paper' / 'BRIEF.md', slug / 'QUESTION.md'):  # QUESTION.md wins
        if anchor.exists():
            fm.update({k: v for k, v in frontmatter(anchor).items() if v})
    title, authors = fm.get('title') or '', fm.get('authors') or []
    if not title:
        sys.exit('QUESTION.md needs a `title:` in its frontmatter')
    fm.setdefault('length_budget', fm.get('length', ''))
    if isinstance(authors, str):
        authors = [s.strip() for s in authors.split(';') if s.strip()]
    sections = sorted((slug / 'paper' / 'sections').glob('*.md'))
    if not sections:
        sys.exit('no sections in paper/sections/')
    body = '\n\n'.join(split(s.read_text())[1].strip() for s in sections)
    body = fill_numbers(body, slug)
    (slug / 'paper' / 'paper.md').write_text('\n'.join([f'# {title}', '', ', '.join(authors), '', body]).rstrip() + '\n')
    print(f'assembled paper/paper.md from {len(sections)} sections')

    problems = []
    n, budget = words(body), re.match(r'\s*(\d[\d,]*)', str(fm.get('length_budget') or ''))
    if budget:
        limit = int(budget.group(1).replace(',', ''))
        print(f'length: {n} words, budget {limit}')
        if n > limit * (1 + a.tolerance):
            problems.append(f'length {n} words exceeds the budget of {limit} by more than {a.tolerance:.0%}')
    else:
        print(f'length: {n} words (no length_budget in QUESTION.md)')
    share = list_share(body)
    print(f'list share: {share:.0%} of prose lines')
    if share > a.max_list_share:
        problems.append(f'list items are {share:.0%} of prose lines (max {a.max_list_share:.0%}): write prose, not lists')
    for p in problems:
        print(('ERROR ' if a.strict else 'WARNING ') + p)
    return 1 if problems and a.strict else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
