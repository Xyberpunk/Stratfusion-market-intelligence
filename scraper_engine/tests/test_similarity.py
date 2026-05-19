from chroma_manager import ChromaManager


class FakeCollection:
    def count(self) -> int:
        return 1

    def query(self, *, query_embeddings, n_results, include):
        return {
            "ids": [["article:1"]],
            "metadatas": [[{"article_id": 1, "source": "moneycontrol"}]],
            "documents": [["infosys warns of slower revenue growth"]],
            "distances": [[0.07]],
        }


def test_chroma_similarity_conversion_without_real_chroma() -> None:
    manager = object.__new__(ChromaManager)
    manager.collection = FakeCollection()
    rows = manager.query_similar(embedding=[0.1, 0.2], n_results=5)
    assert rows[0]["similarity"] == 0.93
    assert rows[0]["metadata"]["article_id"] == 1
