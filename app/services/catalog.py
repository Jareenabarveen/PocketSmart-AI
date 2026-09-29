from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class CatalogItem:
    title: str
    category: str
    platform: str
    price: float
    url: str
    tags: tuple[str, ...]


def search_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    bases = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/chennai/restaurants?query={q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }
    return bases.get(platform, "https://www.google.com/search?q=" + q)


CATALOG = [
    CatalogItem("Minimal LED Ceiling Light", "lighting", "IKEA", 1299, search_url("IKEA", "LED ceiling light"), ("modern", "minimal", "living room")),
    CatalogItem("Smart LED Bulb 9W", "lighting", "Amazon", 499, search_url("Amazon", "smart LED bulb 9W"), ("modern", "smart", "bedroom")),
    CatalogItem("Decorative Table Lamp", "lighting", "Flipkart", 899, search_url("Flipkart", "decorative table lamp"), ("boho", "warm", "bedroom")),
    CatalogItem("Compact Study Table", "furniture", "IKEA", 3999, search_url("IKEA", "compact study table"), ("modern", "minimal", "bedroom")),
    CatalogItem("4-Seater Dining Table", "furniture", "Amazon", 7999, search_url("Amazon", "4 seater dining table"), ("modern", "dining", "kitchen")),
    CatalogItem("Accent Lounge Chair", "furniture", "Flipkart", 5499, search_url("Flipkart", "accent lounge chair"), ("modern", "boho", "living room")),
    CatalogItem("Textured Cushion Set", "decor", "Amazon", 799, search_url("Amazon", "textured cushion set"), ("boho", "modern", "living room")),
    CatalogItem("Framed Abstract Wall Art", "decor", "Flipkart", 1299, search_url("Flipkart", "abstract wall art"), ("modern", "minimal", "living room")),
    CatalogItem("Indoor Plant Pot Set", "decor", "IKEA", 999, search_url("IKEA", "plant pot set"), ("boho", "minimal", "living room")),
    CatalogItem("Veg Catering Combo", "catering", "Swiggy", 450, search_url("Swiggy", "veg catering"), ("birthday", "corporate", "wedding")),
    CatalogItem("Party Biryani Package", "catering", "Zomato", 350, search_url("Zomato", "party biryani catering"), ("birthday", "wedding")),
    CatalogItem("Birthday Balloon Decoration", "decoration", "Amazon", 1499, search_url("Amazon", "birthday balloon decoration kit"), ("birthday", "home")),
    CatalogItem("Corporate Event Decor Kit", "decoration", "Flipkart", 2999, search_url("Flipkart", "corporate event decoration"), ("corporate",)),
    CatalogItem("Budget Banquet Venue", "venue", "OYO", 7000, search_url("OYO", "banquet venue"), ("birthday", "corporate", "wedding")),
    CatalogItem("Party Hall Stay Option", "venue", "OYO", 4500, search_url("OYO", "party hall"), ("birthday",)),
    CatalogItem("Classic Gold-Plated Jhumka", "jewelry", "Amazon", 999, search_url("Amazon", "gold plated jhumka"), ("traditional", "wedding", "festive")),
    CatalogItem("Pearl Drop Earrings", "jewelry", "Flipkart", 1499, search_url("Flipkart", "pearl drop earrings"), ("elegant", "formal", "pastel")),
    CatalogItem("Minimal Layered Necklace", "jewelry", "Amazon", 1799, search_url("Amazon", "minimal layered necklace"), ("modern", "formal", "minimal")),
    CatalogItem("Statement Kundan Set", "jewelry", "Flipkart", 2999, search_url("Flipkart", "kundan jewelry set"), ("traditional", "wedding", "festive")),
]


def find_items(category: str, budget: float, style: str = "", limit: int = 8) -> list[CatalogItem]:
    pool = [x for x in CATALOG if x.category == category and x.price <= budget]
    style = style.lower().strip()
    if style:
        matching = [x for x in pool if style in x.tags]
        pool = matching + [x for x in pool if x not in matching]
    return pool[:limit]
