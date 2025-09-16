"""
Publish Markdown files to Confluence wiki.

Copyright 2022-2025, Levente Hunyadi

:see: https://github.com/hunyadi/md2conf
"""

import logging
import os
import shutil
import unittest
from pathlib import Path

from md2conf.extra import override
from md2conf.mermaid import has_mmdc, render_diagram
from tests.utility import TypedTestCase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s [%(lineno)d] - %(message)s",
)

MERMAID_SOURCE = """
graph TD
  C{ How to contribute? }
  C --> D[ Reporting bugs ]
  C --> E[ Sharing ideas ]
"""


@unittest.skipUnless(has_mmdc(), "mmdc is not available")
@unittest.skipUnless(os.getenv("TEST_MERMAID"), "mermaid tests are disabled")
class TestMermaidRendering(TypedTestCase):
    out_dir: Path

    @override
    def setUp(self) -> None:
        self.maxDiff = 1024

        test_dir = Path(__file__).parent
        parent_dir = test_dir.parent

        self.out_dir = test_dir / "output"
        self.sample_dir = parent_dir / "sample"
        os.makedirs(self.out_dir, exist_ok=True)

    @override
    def tearDown(self) -> None:
        shutil.rmtree(self.out_dir)

    def test_render_simple_svg(self) -> None:
        svg = render_diagram(MERMAID_SOURCE, output_format="svg").decode()

        self.assertIn("transform=", svg)
        self.assertIn("translate(", svg)
        self.assertIn("<rect height=", svg)

    def test_render_simple_png(self) -> None:
        png = render_diagram(MERMAID_SOURCE)
        self.assertIn(b"PNG", png)


if __name__ == "__main__":
    unittest.main()
