#!/usr/bin/env python3
"""Render corpus/coverage.json as the markdown coverage matrix for CORPUS.md (stdlib only).

coverage.json shape:
{
  "aspects": [{"id": "A1", "name": "Memory consolidation", "definition": "...", "queries": ["..."]}],
  "sources": [{"slug": "wang-2026", "label": "Wang et al. 2026"}],
  "cells": {"wang-2026": {"A1": {"score": 2.5, "evidence": ["cite:<uuid>"], "confirmed": true}}}
}

Scores run 0-3 in half steps and render as three circles: filled for each whole point, half for .5, empty
for the rest (2.5 -> filled filled half). Usage:
    render_matrix.py corpus/coverage.json            # prints the matrix section to stdout
    render_matrix.py corpus/coverage.json --thin 2   # also lists aspects with < 2 sources scoring >= 2
    render_matrix.py corpus/coverage.json --pairs 10 # the 10 aspect pairs least often treated together
"""
import argparse
import json
import sys

FULL, HALF, EMPTY = '●', '◐', '○'  # filled, half, empty circle


def glyph(score):
    score = max(0.0, min(3.0, round(float(score) * 2) / 2))
    full = int(score)
    half = 1 if score - full else 0
    return FULL * full + HALF * half + EMPTY * (3 - full - half)


def render(cov, thin_at=None):
    aspects, sources, cells = cov['aspects'], cov['sources'], cov.get('cells', {})
    score = lambda s, a: float(cells.get(s['slug'], {}).get(a['id'], {}).get('score', 0))
    out = ['| Source | ' + ' | '.join(a['id'] for a in aspects) + ' | Breadth |',
           '|---|' + '---|' * len(aspects) + '---|']
    for s in sources:
        row = [glyph(score(s, a)) for a in aspects]
        breadth = sum(score(s, a) >= 2 for a in aspects)
        out.append(f"| {s.get('label', s['slug'])} | " + ' | '.join(row) + f' | {breadth} |')
    depth = [sum(score(s, a) >= 2 for s in sources) for a in aspects]
    total = [sum(score(s, a) for s in sources) for a in aspects]
    out.append('| **Sources >= 2** | ' + ' | '.join(str(d) for d in depth) + ' | |')
    out.append('| **Total score** | ' + ' | '.join(f'{t:g}' for t in total) + ' | |')
    out += ['', 'Legend: ' + f'{glyph(0)} 0 absent · {glyph(1)} 1 mentioned · {glyph(2)} 2 substantive · '
            f'{glyph(3)} 3 central · {HALF} marks a half step.', '']
    out += ['| Id | Aspect | Definition |', '|---|---|---|']
    out += [f"| {a['id']} | {a['name']} | {a.get('definition', '')} |" for a in aspects]
    if thin_at is not None:
        thin = [a for a, d in zip(aspects, depth) if d < thin_at]
        out += ['', f'Thin aspects (< {thin_at} sources scoring >= 2): ' +
                (', '.join(f"{a['id']} {a['name']}" for a in thin) if thin else 'none')]
    return '\n'.join(out) + '\n'


def pairs(cov, limit=10):
    """Aspect pairs ranked by how rarely sources treat both substantively (intersection-gap candidates)."""
    aspects, sources, cells = cov['aspects'], cov['sources'], cov.get('cells', {})
    sub = {a['id']: {s['slug'] for s in sources
                     if float(cells.get(s['slug'], {}).get(a['id'], {}).get('score', 0)) >= 2} for a in aspects}
    rows = []
    for i, a in enumerate(aspects):
        for b in aspects[i + 1:]:
            if not sub[a['id']] or not sub[b['id']]:
                continue  # an aspect nobody treats is a thin aspect, not an intersection gap
            both, either = len(sub[a['id']] & sub[b['id']]), len(sub[a['id']] | sub[b['id']])
            rows.append((both, -either, a, b))
    rows.sort(key=lambda r: (r[0], r[1]))
    out = ['| Pair | Both >= 2 | Either >= 2 |', '|---|---|---|']
    out += [f"| {a['id']} x {b['id']} ({a['name']} / {b['name']}) | {both} | {-neg} |"
            for both, neg, a, b in rows[:limit]]
    return '\n'.join(out) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('coverage_json')
    ap.add_argument('--thin', type=int)
    ap.add_argument('--pairs', type=int, metavar='N', help='print the N least co-treated aspect pairs instead')
    a = ap.parse_args(argv)
    with open(a.coverage_json) as f:
        cov = json.load(f)
    sys.stdout.write(pairs(cov, a.pairs) if a.pairs else render(cov, a.thin))


if __name__ == '__main__':
    main()
