"""Fixture test for the research skill's assets/latex/build.py against the slug layout.

Set RUN_LATEX=1 to also compile with xelatex (slow; needs a TeX toolchain).
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'plugins/z4n4-automated-research/skills/research/assets/latex'
UUID = '0f8d2c4e-1a2b-4c3d-9e8f-123456789abc'

PAPER = f"""---
produced_by: paper
version: 000000000000
updated: 2026-09-28
inputs:
  - paper/BRIEF.md@111111111111
---
# A Fixture Paper

Jane Doe (Example University)

## Abstract

We test the build.

## Introduction

Prior work reports a 12% gain ([Wang et al. 2026: 3-4](cite:{UUID})).

- **First** point with `code`
  - nested *point*
- second point

Table 1. Results by arm.

| Arm | Accuracy |
|---|---|
| A | 0.91 |

## References
"""


class BuildLatexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        slug = pathlib.Path(self.tmp.name) / 'demo'
        (slug / 'corpus').mkdir(parents=True)
        self.latex = slug / 'paper/latex'
        self.latex.mkdir(parents=True)
        (slug / 'paper/paper.md').write_text(PAPER)
        (slug / 'corpus/metadata.json').write_text(json.dumps({'wang-2026': {
            'title': 'Scaling & Things', 'authors': ['Wang, Li', 'Smith, Ann'], 'year': 2026,
            'full_reference': 'Wang, Li, and Ann Smith. 2026. "Scaling & Things." arXiv:2601.00001.'}}))
        for f in ('build.py', 'preamble.tex'):
            shutil.copy(ASSETS / f, self.latex / f)
        (self.latex / 'refs.json').write_text(json.dumps({'title': 'A Fixture Paper', 'author': 'Jane Doe',
            'citations': {'Wang et al. 2026': 'wang-2026'}}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_converts_slug_layout(self):
        out = subprocess.run([sys.executable, 'build.py'], cwd=self.latex, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        tex = (self.latex / 'paper.tex').read_text()
        self.assertIn('(Wang et al. 2026: 3-4)', tex)
        self.assertIn(r'\textbf{Table 1.} Results by arm.', tex)
        self.assertIn(r'\begin{longtable}', tex)
        self.assertIn(r'\item \textbf{First} point with \texttt{code}', tex)
        self.assertIn(r'\item nested \emph{point}', tex)
        self.assertEqual(tex.count(r'\begin{itemize}'), 2)
        self.assertIn('We test the build.', tex)
        self.assertNotIn('produced_by', tex)
        self.assertNotIn('Jane Doe (Example University)', tex)  # byline comes from refs.json, not the body
        self.assertIn(r'\section*{References}', tex)
        self.assertIn("Wang, Li, and Ann Smith. 2026. ``Scaling \\& Things.'' arXiv:2601.00001.", tex)

    def test_essay_without_abstract(self):
        paper = self.latex.parent / 'paper.md'
        paper.write_text(PAPER.replace('## Abstract\n\nWe test the build.\n\n', ''))
        out = subprocess.run([sys.executable, 'build.py'], cwd=self.latex, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        tex = (self.latex / 'paper.tex').read_text()
        self.assertNotIn(r'\begin{abstract}', tex)
        self.assertIn(r'\section*{Introduction}', tex)
        self.assertNotIn('Jane Doe (Example University)', tex)  # the byline line is not body text

    def test_citations_without_pages(self):
        (self.latex / 'refs.json').write_text(json.dumps({'title': 'T', 'author': 'A', 'cite_pages': False,
            'citations': {'Wang et al. 2026': 'wang-2026'}, 'manual': {'Wang et al. 2026': 'Wang, L. 2026. Styled.'}}))
        out = subprocess.run([sys.executable, 'build.py'], cwd=self.latex, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        tex = (self.latex / 'paper.tex').read_text()
        self.assertIn('(Wang et al. 2026)', tex)
        self.assertIn('Wang, L. 2026. Styled.', tex)

    def test_manual_reference_for_software(self):
        paper = self.latex.parent / 'paper.md'
        paper.write_text(PAPER.replace('- second point', '- second point, modelled in OxCal ([Bronk Ramsey 2009](ref:manual))'))
        (self.latex / 'refs.json').write_text(json.dumps({'title': 'T', 'author': 'A',
            'citations': {'Wang et al. 2026': 'wang-2026'}, 'manual': {'Bronk Ramsey 2009': 'Bronk Ramsey, C. 2009. OxCal.'}}))
        out = subprocess.run([sys.executable, 'build.py'], cwd=self.latex, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        tex = (self.latex / 'paper.tex').read_text()
        self.assertIn('(Bronk Ramsey 2009)', tex)
        self.assertIn('Bronk Ramsey, C. 2009. OxCal.', tex)
        self.assertEqual(tex.count(r'\item '), 2 + 3)  # two references plus the three list items

    def test_unmapped_citation_fails_clearly(self):
        (self.latex / 'refs.json').write_text(json.dumps({'title': 'T', 'author': 'A', 'citations': {}}))
        out = subprocess.run([sys.executable, 'build.py'], cwd=self.latex, capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn('Wang et al. 2026', out.stderr)

    @unittest.skipUnless(os.environ.get('RUN_LATEX') and shutil.which('xelatex'), 'set RUN_LATEX=1 with xelatex installed')
    def test_compiles_pdf(self):
        subprocess.run([sys.executable, 'build.py'], cwd=self.latex, check=True, capture_output=True)
        for _ in range(2):
            subprocess.run(['xelatex', '-interaction=nonstopmode', 'paper.tex'], cwd=self.latex, capture_output=True, timeout=300)
        self.assertTrue((self.latex / 'paper.pdf').exists())


if __name__ == '__main__':
    unittest.main()
