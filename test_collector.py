"""
Collector Test
Her kaynağın tek tek çalışıp çalışmadığını gösterir.
"""

from sources.hn_fetcher import fetch_hacker_news
from sources.github_fetcher import fetch_github_trending
from sources.trends_fetcher import fetch_google_trends
from sources.lobsters_fetcher import fetch_lobsters
from sources.producthunt_fetcher import fetch_producthunt
from sources.betalists_fetcher import fetch_betalist
from sources.reddit_fetcher import fetch_reddit_posts


def test_source(name, func):
    print("=" * 60)
    print(name)

    try:
        posts = func(limit=3)

        print("Toplanan :", len(posts))

        for p in posts:
            print("-", p.get("title", "")[:70])

    except Exception as e:
        print("HATA:", e)


def main():

    test_source("Hacker News", fetch_hacker_news)

    test_source("GitHub Trending", fetch_github_trending)

    test_source("Google Trends", fetch_google_trends)

    test_source("Lobsters", fetch_lobsters)

    test_source("Product Hunt", fetch_producthunt)

    test_source("BetaList", fetch_betalist)

    test_source("Reddit", fetch_reddit_posts)


if __name__ == "__main__":
    main()
