"""Mock Amazon product data for MVP development.

Replace with real API calls (Rainforest, Apify, Oxylabs, etc.) when keys are available.
"""

from __future__ import annotations

import random

_NICHE_CATALOG: dict[str, list[dict]] = {
    "Self-Help": [
        {"asin": "B0CX1A2B3C", "title": "Atomic Habits for Kindle Readers", "author": "James R.", "price": 9.99, "bsr": 1_250, "rating": 4.6, "review_count": 12_340, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CX2D4E5F", "title": "The 5 AM Club: Morning Mastery", "author": "Robin S.", "price": 11.99, "bsr": 3_400, "rating": 4.3, "review_count": 8_900, "category": "Self-Help", "kindle_unlimited": False},
        {"asin": "B0CX3G6H7I", "title": "Mindset Shift: Think and Grow", "author": "Carol D.", "price": 7.99, "bsr": 8_200, "rating": 4.1, "review_count": 4_560, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CX4J8K9L", "title": "Deep Work for Creative Minds", "author": "Cal N.", "price": 12.99, "bsr": 15_600, "rating": 4.5, "review_count": 6_780, "category": "Self-Help", "kindle_unlimited": False},
        {"asin": "B0CX5M0N1O", "title": "Emotional Intelligence 2.0 Guide", "author": "Travis B.", "price": 8.99, "bsr": 22_300, "rating": 4.2, "review_count": 3_450, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CX6P2Q3R", "title": "Stoicism for Modern Life", "author": "Ryan H.", "price": 6.99, "bsr": 34_500, "rating": 4.4, "review_count": 5_670, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CX7S4T5U", "title": "The Power of Now: Daily Practice", "author": "Eckhart T.", "price": 10.99, "bsr": 45_600, "rating": 4.7, "review_count": 15_890, "category": "Self-Help", "kindle_unlimited": False},
        {"asin": "B0CX8V6W7X", "title": "Grit: The Art of Perseverance", "author": "Angela D.", "price": 9.49, "bsr": 56_200, "rating": 4.0, "review_count": 2_340, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CX9Y8Z1A", "title": "Boundary Setting for Empaths", "author": "Dr. Judith O.", "price": 5.99, "bsr": 67_800, "rating": 4.3, "review_count": 1_890, "category": "Self-Help", "kindle_unlimited": True},
        {"asin": "B0CXA0B1C2", "title": "Digital Minimalism Handbook", "author": "Cal N.", "price": 8.49, "bsr": 78_900, "rating": 4.1, "review_count": 3_210, "category": "Self-Help", "kindle_unlimited": False},
    ],
    "Romance": [
        {"asin": "B0RD1A2B3C", "title": "Hearts in the Highlands", "author": "Emily B.", "price": 4.99, "bsr": 2_100, "rating": 4.4, "review_count": 9_870, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD2D4E5F", "title": "The Duke's Secret Bride", "author": "Julia Q.", "price": 3.99, "bsr": 5_300, "rating": 4.2, "review_count": 7_650, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD3G6H7I", "title": "Summer at the Lake House", "author": "Mary K.", "price": 5.99, "bsr": 11_400, "rating": 4.5, "review_count": 5_430, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD4J8K9L", "title": "Second Chance in Paris", "author": "Sarah M.", "price": 6.99, "bsr": 18_700, "rating": 4.3, "review_count": 4_210, "category": "Romance", "kindle_unlimited": False},
        {"asin": "B0RD5M0N1O", "title": "The Billionaire's Proposal", "author": "Lauren L.", "price": 3.49, "bsr": 28_900, "rating": 4.0, "review_count": 6_780, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD6P2Q3R", "title": "Cowboy's Christmas Wish", "author": "Debbie M.", "price": 4.49, "bsr": 35_200, "rating": 4.6, "review_count": 3_890, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD7S4T5U", "title": "Enemies to Lovers: NYC", "author": "Ali H.", "price": 5.49, "bsr": 42_100, "rating": 4.1, "review_count": 2_560, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RD8V6W7X", "title": "Love in the Time of WiFi", "author": "Penny R.", "price": 4.99, "bsr": 55_400, "rating": 4.2, "review_count": 1_980, "category": "Romance", "kindle_unlimited": False},
        {"asin": "B0RD9Y8Z1A", "title": "The Matchmaker's List", "author": "Sonya L.", "price": 7.99, "bsr": 68_300, "rating": 4.4, "review_count": 3_120, "category": "Romance", "kindle_unlimited": True},
        {"asin": "B0RDA0B1C2", "title": "Forbidden Highland Love", "author": "Hannah H.", "price": 3.99, "bsr": 82_500, "rating": 4.0, "review_count": 2_450, "category": "Romance", "kindle_unlimited": True},
    ],
    "Science Fiction": [
        {"asin": "B0SF1A2B3C", "title": "The Last Colony Ship", "author": "Andy W.", "price": 6.99, "bsr": 3_200, "rating": 4.5, "review_count": 8_900, "category": "Science Fiction", "kindle_unlimited": False},
        {"asin": "B0SF2D4E5F", "title": "Neural Link: Year 2150", "author": "Blake C.", "price": 5.99, "bsr": 7_800, "rating": 4.3, "review_count": 6_540, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SF3G6H7I", "title": "Mars Rebellion Chronicles", "author": "Kim S.R.", "price": 8.99, "bsr": 14_200, "rating": 4.6, "review_count": 5_670, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SF4J8K9L", "title": "Quantum Garden", "author": "Hannu R.", "price": 7.49, "bsr": 23_400, "rating": 4.1, "review_count": 3_890, "category": "Science Fiction", "kindle_unlimited": False},
        {"asin": "B0SF5M0N1O", "title": "AI Uprising: Silicon Souls", "author": "Martha W.", "price": 4.99, "bsr": 31_500, "rating": 4.4, "review_count": 4_210, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SF6P2Q3R", "title": "Starfarer's Handbook", "author": "Becky C.", "price": 9.99, "bsr": 44_800, "rating": 4.2, "review_count": 2_780, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SF7S4T5U", "title": "The Void Between Stars", "author": "Adrian T.", "price": 6.49, "bsr": 52_300, "rating": 4.0, "review_count": 1_560, "category": "Science Fiction", "kindle_unlimited": False},
        {"asin": "B0SF8V6W7X", "title": "Cyberpunk Dreams", "author": "William G.", "price": 5.49, "bsr": 63_700, "rating": 4.3, "review_count": 3_340, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SF9Y8Z1A", "title": "Time Loop Detective", "author": "Annalee N.", "price": 7.99, "bsr": 76_200, "rating": 4.5, "review_count": 2_890, "category": "Science Fiction", "kindle_unlimited": True},
        {"asin": "B0SFA0B1C2", "title": "The Expanse of Andromeda", "author": "James C.", "price": 8.49, "bsr": 89_400, "rating": 4.1, "review_count": 1_990, "category": "Science Fiction", "kindle_unlimited": False},
    ],
    "Business & Money": [
        {"asin": "B0BM1A2B3C", "title": "The Lean Startup Playbook", "author": "Eric R.", "price": 12.99, "bsr": 1_800, "rating": 4.4, "review_count": 11_200, "category": "Business & Money", "kindle_unlimited": False},
        {"asin": "B0BM2D4E5F", "title": "Passive Income Blueprint 2024", "author": "Rachel R.", "price": 9.99, "bsr": 4_500, "rating": 4.1, "review_count": 6_780, "category": "Business & Money", "kindle_unlimited": True},
        {"asin": "B0BM3G6H7I", "title": "E-Commerce Mastery: FBA Guide", "author": "Kevin D.", "price": 14.99, "bsr": 9_800, "rating": 4.3, "review_count": 4_560, "category": "Business & Money", "kindle_unlimited": False},
        {"asin": "B0BM4J8K9L", "title": "Real Estate Investing for Beginners", "author": "Brandon T.", "price": 11.99, "bsr": 16_400, "rating": 4.5, "review_count": 8_900, "category": "Business & Money", "kindle_unlimited": True},
        {"asin": "B0BM5M0N1O", "title": "Copywriting Secrets That Sell", "author": "Jim E.", "price": 7.99, "bsr": 25_600, "rating": 4.2, "review_count": 3_210, "category": "Business & Money", "kindle_unlimited": True},
        {"asin": "B0BM6P2Q3R", "title": "Financial Freedom After 40", "author": "Suze O.", "price": 10.99, "bsr": 38_900, "rating": 4.0, "review_count": 2_450, "category": "Business & Money", "kindle_unlimited": False},
        {"asin": "B0BM7S4T5U", "title": "Day Trading for a Living", "author": "Andrew A.", "price": 8.49, "bsr": 47_200, "rating": 4.3, "review_count": 5_670, "category": "Business & Money", "kindle_unlimited": True},
        {"asin": "B0BM8V6W7X", "title": "The Solopreneur's Guide", "author": "Chris G.", "price": 6.99, "bsr": 58_100, "rating": 4.1, "review_count": 1_890, "category": "Business & Money", "kindle_unlimited": True},
        {"asin": "B0BM9Y8Z1A", "title": "Negotiation: Getting to Yes", "author": "Roger F.", "price": 9.49, "bsr": 71_300, "rating": 4.6, "review_count": 7_540, "category": "Business & Money", "kindle_unlimited": False},
        {"asin": "B0BMA0B1C2", "title": "Remote Work Revolution", "author": "Tsedal N.", "price": 13.99, "bsr": 85_600, "rating": 4.2, "review_count": 2_890, "category": "Business & Money", "kindle_unlimited": True},
    ],
    "Health & Fitness": [
        {"asin": "B0HF1A2B3C", "title": "The Carnivore Code", "author": "Paul S.", "price": 11.99, "bsr": 2_400, "rating": 4.5, "review_count": 9_120, "category": "Health & Fitness", "kindle_unlimited": False},
        {"asin": "B0HF2D4E5F", "title": "Intermittent Fasting Made Easy", "author": "Jason F.", "price": 6.99, "bsr": 6_100, "rating": 4.2, "review_count": 7_340, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HF3G6H7I", "title": "Yoga for Desk Workers", "author": "Adriene M.", "price": 8.99, "bsr": 12_800, "rating": 4.6, "review_count": 4_560, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HF4J8K9L", "title": "Gut Health Reset", "author": "Dr. Will B.", "price": 10.99, "bsr": 19_500, "rating": 4.3, "review_count": 5_890, "category": "Health & Fitness", "kindle_unlimited": False},
        {"asin": "B0HF5M0N1O", "title": "Sleep Smarter: 21 Strategies", "author": "Shawn S.", "price": 7.49, "bsr": 27_300, "rating": 4.4, "review_count": 3_670, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HF6P2Q3R", "title": "Keto Meal Prep Cookbook", "author": "Maria E.", "price": 5.99, "bsr": 36_700, "rating": 4.1, "review_count": 6_210, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HF7S4T5U", "title": "Running: From 5K to Marathon", "author": "Hal H.", "price": 9.99, "bsr": 48_900, "rating": 4.0, "review_count": 2_340, "category": "Health & Fitness", "kindle_unlimited": False},
        {"asin": "B0HF8V6W7X", "title": "Mental Health Toolkit", "author": "Dr. Julie S.", "price": 12.49, "bsr": 57_400, "rating": 4.5, "review_count": 4_120, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HF9Y8Z1A", "title": "Plant-Based Athlete", "author": "Matt F.", "price": 8.99, "bsr": 69_200, "rating": 4.2, "review_count": 1_780, "category": "Health & Fitness", "kindle_unlimited": True},
        {"asin": "B0HFA0B1C2", "title": "Strength Training Over 50", "author": "Mark R.", "price": 7.99, "bsr": 81_500, "rating": 4.3, "review_count": 3_450, "category": "Health & Fitness", "kindle_unlimited": False},
    ],
}

# Sample 3-star reviews for gap analysis
_MOCK_REVIEWS: list[dict] = [
    {"reviewer": "ReaderA", "rating": 3, "title": "Good but missing workbook", "body": "The concepts are solid but I wish there were exercises or a workbook section to actually practice what's taught. Just reading isn't enough for real change.", "date": "2024-08-15", "helpful_count": 45},
    {"reviewer": "ReaderB", "rating": 3, "title": "Needed more real examples", "body": "Theory is fine but where are the case studies? I wanted to see real people applying these strategies. The book feels too academic without practical examples.", "date": "2024-07-22", "helpful_count": 32},
    {"reviewer": "ReaderC", "rating": 3, "title": "Outdated information", "body": "Some of the advice feels like it was written 5 years ago. The digital landscape has changed dramatically. Needs a 2024 update with current tools and platforms.", "date": "2024-09-01", "helpful_count": 28},
    {"reviewer": "ReaderD", "rating": 3, "title": "Too short on implementation", "body": "Great overview but the 'how-to' sections are way too brief. I need step-by-step instructions, not just high-level overviews. More depth please.", "date": "2024-06-18", "helpful_count": 51},
    {"reviewer": "ReaderE", "rating": 3, "title": "Missing the beginner angle", "body": "Written for people who already have experience. Complete beginners will be lost. Should have included a fundamentals chapter.", "date": "2024-08-30", "helpful_count": 39},
    {"reviewer": "ReaderF", "rating": 3, "title": "No audiobook companion", "body": "The content is decent but I learn better by listening. Many competing books offer audio versions or companion podcasts. This one doesn't.", "date": "2024-07-05", "helpful_count": 22},
    {"reviewer": "ReaderG", "rating": 3, "title": "Templates would help", "body": "The frameworks discussed are useful but without downloadable templates or checklists, it's hard to actually use them. A companion resource library would make this 5 stars.", "date": "2024-09-10", "helpful_count": 67},
    {"reviewer": "ReaderH", "rating": 3, "title": "Repetitive middle chapters", "body": "First three chapters are excellent. Then it starts repeating the same points with different words. Could have been 150 pages instead of 300.", "date": "2024-08-02", "helpful_count": 41},
    {"reviewer": "ReaderI", "rating": 3, "title": "Missing digital tools section", "body": "In 2024, any book in this space should cover the relevant apps and software tools. Zero mention of technology integration.", "date": "2024-07-28", "helpful_count": 35},
    {"reviewer": "ReaderJ", "rating": 3, "title": "Good start, weak finish", "body": "The early chapters set up a fantastic framework but the later chapters don't deliver on the promise. The conclusion feels rushed with no action plan.", "date": "2024-09-05", "helpful_count": 29},
]


def get_available_categories() -> list[str]:
    return list(_NICHE_CATALOG.keys())


def fetch_mock_products(category: str, count: int = 50) -> list[dict]:
    """Return mock products for a category, generating additional ones if needed."""
    base = _NICHE_CATALOG.get(category, _NICHE_CATALOG["Self-Help"])

    if len(base) >= count:
        return base[:count]

    products = list(base)
    while len(products) < count:
        template = random.choice(base)
        variant = dict(template)
        suffix = len(products)
        variant["asin"] = f"B0GEN{suffix:04d}XX"
        variant["title"] = f"{template['title']} (Vol. {suffix})"
        variant["bsr"] = random.randint(1_000, 100_000)
        variant["price"] = round(random.uniform(2.99, 14.99), 2)
        variant["rating"] = round(random.uniform(3.5, 4.8), 1)
        variant["review_count"] = random.randint(500, 15_000)
        products.append(variant)

    return products[:count]


def fetch_mock_reviews(asin: str, count: int = 10) -> list[dict]:
    """Return mock reviews prioritizing 3-star ratings."""
    reviews = list(_MOCK_REVIEWS)
    while len(reviews) < count:
        template = random.choice(_MOCK_REVIEWS)
        variant = dict(template)
        variant["reviewer"] = f"Reader_{len(reviews)}"
        reviews.append(variant)
    return reviews[:count]
