import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_team_chat.database import Database
from agent_team_chat.docs import register_doc, search_docs, get_doc_chunk


class TestDocs(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test_chunking_and_search(self):
        # Create a long text ~ 2000 words
        para = "This is a test paragraph about alpha beta gamma delta. "
        text = " ".join([para for _ in range(1200)])
        res = register_doc(self.db, title="Test Doc", text=text)
        self.assertIn("doc_id", res)
        self.assertGreaterEqual(res["chunks"], 2)

        results = search_docs(self.db, query="alpha", limit=5)
        self.assertTrue(len(results) >= 1)
        doc_id = res["doc_id"]
        chunk = get_doc_chunk(self.db, doc_id=doc_id, chunk_index=0)
        self.assertIsNotNone(chunk)
        self.assertIn("text", chunk)


if __name__ == "__main__":
    unittest.main()
