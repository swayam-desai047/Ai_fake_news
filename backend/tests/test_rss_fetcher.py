import httpx

from services.rss_fetcher import clean_html, dedupe, fetch_articles, normalise_url, parse_feed

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Test</title>
<item><title>First &amp; story</title><link>https://ex.com/a?utm=1</link>
<description>&lt;p&gt;Body &lt;b&gt;text&lt;/b&gt; here.&lt;/p&gt;</description>
<pubDate>Tue, 24 Nov 2026 10:30:00 GMT</pubDate></item>
<item><title>Headline only</title><link>https://ex.com/b</link></item>
<item><title></title><link>https://ex.com/c</link></item>
</channel></rss>"""


def test_parse_feed_extracts_fields():
    items = parse_feed(RSS, "Example", "technology")
    assert len(items) == 2  # untitled entry dropped
    a = items[0]
    assert a["title"] == "First & story"
    assert a["content_summary"] == "Body text here."
    assert a["published_at"] == "2026-11-24T10:30:00+00:00"
    assert a["category"] == "technology" and a["source_domain"] == "Example"
    assert items[1]["content_summary"] == ""  # no title fallback
    assert items[1]["published_at"] is None


def test_clean_html_and_url_normalisation():
    assert clean_html("<p>a <i>b</i></p>\n\n c") == "a b c"
    assert normalise_url("HTTPS://Ex.com/a/?x=1#f") == "https://ex.com/a"


def test_dedupe_by_url_and_title():
    rows = [
        {"title": "A story", "source_url": "https://x.com/1"},
        {"title": "A  STORY!", "source_url": "https://y.com/2"},
        {"title": "Other", "source_url": "https://x.com/1?ref=rss"},
        {"title": "Third", "source_url": "https://z.com/3"},
    ]
    assert [r["title"] for r in dedupe(rows)] == ["A story", "Third"]


def test_failed_feed_does_not_stop_the_run():
    def handler(request):
        if "bad" in str(request.url):
            return httpx.Response(500)
        return httpx.Response(200, content=RSS)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    articles, failed = fetch_articles({"general": {"Good": "https://good/rss", "Bad": "https://bad/rss"}}, client=client)
    assert failed == ["Bad"]
    assert len(articles) == 2
