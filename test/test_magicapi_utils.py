import unittest

from magicapi_tools.utils.knowledge_base import get_syntax, list_examples, get_docs
from mcp.magicapi_assistant import _filter_nodes, _nodes_to_csv


class KnowledgeBaseTest(unittest.TestCase):
    def test_syntax_topic_exists(self):
        syntax = get_syntax("keywords")
        self.assertIsNotNone(syntax)
        self.assertIn("sections", syntax)

    def test_examples_filter(self):
        examples = list_examples("db")
        self.assertTrue(any("分页" in ex["title"] for ex in examples))

    def test_docs_summary(self):
        docs = get_docs(index_only=False)
        self.assertIn("index", docs)
        self.assertIn("summary", docs)


class TreeHelperTest(unittest.TestCase):
    def test_filter_nodes_regex(self):
        nodes = [
            {"name": "用户查询", "path": "/user/list"},
            {"name": "订单创建", "path": "/order/create"},
        ]
        filtered = _filter_nodes(nodes, "订单")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["path"], "/order/create")

    def test_nodes_to_csv_quotes(self):
        nodes = [
            {"name": "导出,数据", "path": "/export", "method": "GET", "type": "api", "id": "1"}
        ]
        csv = _nodes_to_csv(nodes)
        self.assertIn('"导出,数据"', csv)
        self.assertIn("/export", csv)


if __name__ == "__main__":
    unittest.main()
