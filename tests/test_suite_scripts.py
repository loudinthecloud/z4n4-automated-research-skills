"""Tests for scripts/render_matrix.py and scripts/assemble.py of the research skill."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/z4n4-automated-research/skills/research/scripts'
sys.path.insert(0, str(SCRIPTS))
import render_matrix  # noqa: E402

COV = {
    'aspects': [{'id': 'A1', 'name': 'Consolidation', 'definition': 'd1'},
                {'id': 'A2', 'name': 'Interference', 'definition': 'd2'},
                {'id': 'A3', 'name': 'Replay', 'definition': 'd3'}],
    'sources': [{'slug': 's1', 'label': 'Wang 2026'}, {'slug': 's2', 'label': 'Lee 2025'}],
    'cells': {'s1': {'A1': {'score': 2.5}, 'A2': {'score': 2}},
              's2': {'A1': {'score': 3}, 'A3': {'score': 0.5}}},
}


class RenderMatrixTest(unittest.TestCase):
    def test_glyphs_half_steps(self):
        g = render_matrix.glyph
        self.assertEqual(g(0), '○○○')
        self.assertEqual(g(2.5), '●●◐')
        self.assertEqual(g(3), '●●●')
        self.assertEqual(g(0.5), '◐○○')
        self.assertEqual(g(1.3), '●◐○')  # rounds to the nearest half step (1.5)
        self.assertEqual(g(7), g(3))

    def test_matrix_rows_totals_and_thin(self):
        md = render_matrix.render(COV, thin_at=2)
        self.assertIn('| Wang 2026 | ●●◐ | ●●○ | ○○○ | 2 |', md)
        self.assertIn('| **Sources >= 2** | 2 | 1 | 0 | |', md)
        self.assertIn('Thin aspects (< 2 sources scoring >= 2): A2 Interference, A3 Replay', md)

    def test_pairs_rank_rare_intersections_first(self):
        cov = json.loads(json.dumps(COV))
        cov['sources'].append({'slug': 's3', 'label': 'Kim 2024'})
        cov['cells']['s3'] = {'A3': {'score': 2}}
        lines = [l for l in render_matrix.pairs(cov).splitlines() if l.startswith('| A')]
        self.assertTrue(lines[0].startswith('| A1 x A3'), lines)  # never co-treated, widest reach first
        self.assertTrue(lines[-1].startswith('| A1 x A2'), lines)  # co-treated by s1: least gap-like
        self.assertIn('| A1 x A2 (Consolidation / Interference) | 1 | 2 |', '\n'.join(lines))

    def test_pairs_skip_untreated_aspects(self):
        self.assertNotIn('A3', render_matrix.pairs(COV))  # A3 has no source >= 2: thin, not intersection

    def test_cli(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(COV, f)
        out = subprocess.run([sys.executable, str(SCRIPTS / 'render_matrix.py'), f.name, '--thin', '2'],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('Legend:', out.stdout)


class AssembleTest(unittest.TestCase):
    def slug(self, tmp, sections, budget='1000 words', numbers=None):
        slug = pathlib.Path(tmp)
        (slug / 'paper/sections').mkdir(parents=True)
        (slug / 'QUESTION.md').write_text('---\ntitle: On Memory\nauthors:\n  - Jane Doe (MIT)\n  - John Smith (Stanford)\n'
                                          f'length_budget: {budget}\n---\n# Question\n')
        for name, text in sections.items():
            (slug / 'paper/sections' / name).write_text(text)
        if numbers is not None:
            (slug / 'results').mkdir()
            (slug / 'results/numbers.json').write_text(json.dumps(numbers))
        return slug

    def assemble(self, slug, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / 'assemble.py'), str(slug), *args],
                              capture_output=True, text=True)

    def test_title_block_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug = self.slug(tmp, {'02-introduction.md': '## Introduction\n\nIntro.\n',
                                   '01-abstract.md': '---\nproduced_by: x\n---\n## Abstract\n\nAbs.\n'})
            out = self.assemble(slug)
            self.assertEqual(out.returncode, 0, out.stderr)
            paper = (slug / 'paper/paper.md').read_text()
            self.assertTrue(paper.startswith('# On Memory\n\nJane Doe (MIT), John Smith (Stanford)\n'))
            self.assertLess(paper.index('## Abstract'), paper.index('## Introduction'))
            self.assertNotIn('produced_by', paper)

    def test_numbers_filled_from_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug = self.slug(tmp, {'01-abstract.md': '## Abstract\n\nP = {{num:h1_p}}.\n'}, numbers={'h1_p': '0.76'})
            self.assertEqual(self.assemble(slug).returncode, 0)
            self.assertIn('P = 0.76.', (slug / 'paper/paper.md').read_text())

    def test_unknown_number_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug = self.slug(tmp, {'01-abstract.md': '## Abstract\n\nP = {{num:nope}}.\n'}, numbers={})
            out = self.assemble(slug)
            self.assertNotEqual(out.returncode, 0)
            self.assertIn('nope', out.stderr)

    def test_length_and_list_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = '## Abstract\n\n' + 'word ' * 40 + '\n\n- one\n- two\n- three\n'
            slug = self.slug(tmp, {'01-abstract.md': body}, budget='20 words')
            out = self.assemble(slug)
            self.assertEqual(out.returncode, 0)  # warnings only
            self.assertIn('WARNING length', out.stdout)
            self.assertIn('WARNING list items', out.stdout)
            self.assertNotEqual(self.assemble(slug, '--strict').returncode, 0)

    def test_older_project_uses_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug = pathlib.Path(tmp)
            (slug / 'paper/sections').mkdir(parents=True)
            (slug / 'paper/BRIEF.md').write_text('---\ntitle: Old Layout\nauthors:\n  - Jane Doe (MIT)\nlength: 30 words\n---\n')
            (slug / 'paper/sections/01-abstract.md').write_text('## Abstract\n\n' + 'word ' * 50 + '\n')
            out = self.assemble(slug)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertTrue((slug / 'paper/paper.md').read_text().startswith('# Old Layout\n'))
            self.assertIn('budget 30', out.stdout)


if __name__ == '__main__':
    unittest.main()
