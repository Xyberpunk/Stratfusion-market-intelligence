from utils.hashing import hash_content, hash_url, normalize_text, normalize_url


def test_normalize_url_removes_query_trailing_slash_and_lowercases_host() -> None:
    url = "HTTPS://WWW.MONEYCONTROL.COM/news/business/markets/story/?utm_source=x&id=1#section"
    assert normalize_url(url) == "https://www.moneycontrol.com/news/business/markets/story"


def test_hash_url_uses_normalized_url() -> None:
    left = hash_url("https://example.com/Article/?utm_source=a")
    right = hash_url("https://example.com/Article")
    assert left == right


def test_normalize_text_compacts_whitespace_and_casefolds() -> None:
    assert normalize_text(" Infosys\u00a0 cuts\n\n FY Guidance ") == "infosys cuts fy guidance"


def test_hash_content_uses_normalized_text() -> None:
    assert hash_content("Infosys cuts FY guidance") == hash_content(" infosys   cuts fy guidance ")
