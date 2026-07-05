"""
Seed a rich demo dataset across 10 categories.

Design notes on images/logos (read this before adding your own data):
- `image_url` = a product/subject PHOTO. For real products we use picsum.photos
  placeholders (random stock photos) so cards aren't blank -- swap for real
  photos before publishing. For Footballers we deliberately leave this blank;
  see below.
- `logo_url` = the REAL brand/company logo, fetched live by domain from
  Hunter's free Logo API (https://hunter.io/api/logo, the maintained
  successor to Clearbit's now-discontinued logo API). No key needed. If a
  domain doesn't resolve, the <img onerror> in the templates just hides it.
  Logos remain trademarks of their owners -- this is the standard nominative
  use pattern comparison sites rely on to identify what's being compared,
  but it's your responsibility to ensure your use complies with each
  trademark holder's policies. See README.
- Footballers get NEITHER a photo nor a logo -- just an initials avatar
  (see Item.initials). Real people's photos raise likeness/publicity-rights
  issues beyond simple brand-logo nominative use, and "current club" changes
  every transfer window, so we don't fake either one.
- Companies/Telecom/Construction/Universities/Clothing stat figures (revenue,
  employees, rankings, achievements) are ILLUSTRATIVE placeholders, not
  verified data -- several were checked against live search in July 2026
  (notably the footballers' stats, mid-World-Cup) but ALL of it will drift.
  Verify before publishing. See README.
"""
from django.core.management.base import BaseCommand
from compare.models import Category, Spec, Item, SpecValue, Review, Comparison

NAMES = ["Chidi", "Ngozi", "Emeka", "Fatima", "Tunde", "Amaka",
         "Ibrahim", "Blessing", "Uche", "Kemi", "Yusuf", "Chioma"]

REVIEW_POOL = [
    ("{n} is worth the money — no regrets picking this one.", 5),
    ("Been using {n} for a while now, does the job well.", 4),
    ("{n} has a few quirks but overall I'm satisfied.", 4),
    ("Not bad, though I compared a couple of options before deciding.", 3),
    ("{n} exceeded what I expected for this price range.", 5),
]

LOGO_BASE = "https://logos.hunter.io/"
PHOTO_BASE = "https://picsum.photos/seed/"


def format_spec_text(value):
    if isinstance(value, float) and value == int(value):
        value = int(value)
    if isinstance(value, int) and abs(value) >= 1000:
        return f"{value:,}"
    return str(value)


def seed_reviews(item, count=2):
    for i in range(count):
        template, rating = REVIEW_POOL[(item.id + i) % len(REVIEW_POOL)]
        name = NAMES[(item.id + i * 3) % len(NAMES)]
        comment = template.format(n=item.name)
        Review.objects.get_or_create(item=item, name=name, comment=comment, defaults={"rating": rating})


def make_category(name, slug, icon, description, specs):
    """specs: list of (name, unit, higher_is_better). Returns (category, [spec names in order], {name: Spec obj})."""
    category, _ = Category.objects.get_or_create(name=name, slug=slug, defaults={"icon": icon, "description": description})
    spec_objs = {}
    spec_names = []
    for i, (sname, unit, higher) in enumerate(specs):
        s, _ = Spec.objects.get_or_create(
            category=category, name=sname,
            defaults={"unit": unit, "higher_is_better": higher, "order": i},
        )
        spec_objs[sname] = s
        spec_names.append(sname)
    return category, spec_names, spec_objs


def build_items(category, spec_names, spec_objs, rows):
    """rows: list of (name, brand, price, score, photo_key_or_None, domain_or_None,
    summary, [pros], [cons], (values in same order as spec_names)).
    Positional spec values (not dict keys) so a typo can't silently point at
    the wrong spec -- order is guaranteed to match spec_names."""
    items = {}
    for name, brand, price, score, photo_key, domain, summary, pros, cons, values in rows:
        item, _ = Item.objects.get_or_create(category=category, name=name, defaults={
            "brand": brand,
            "price": price,
            "score": score,
            "image_url": f"{PHOTO_BASE}{photo_key}/480/320" if photo_key else "",
            "logo_url": f"{LOGO_BASE}{domain}" if domain else "",
            "summary": summary,
            "description": summary,
            "pros": "\n".join(pros),
            "cons": "\n".join(cons),
        })
        assert len(values) == len(spec_names), f"{name}: expected {len(spec_names)} spec values, got {len(values)}"
        for sname, value in zip(spec_names, values):
            SpecValue.objects.get_or_create(
                item=item, spec=spec_objs[sname],
                defaults={"value_text": format_spec_text(value), "value_numeric": float(value)},
            )
        seed_reviews(item)
        items[name] = item
    return items


def link(category, item_a, item_b, views, votes_a, votes_b):
    lo, hi = (item_a, item_b) if item_a.id < item_b.id else (item_b, item_a)
    c, _ = Comparison.objects.get_or_create(category=category, item_a=lo, item_b=hi)
    Comparison.objects.filter(pk=c.pk).update(views=views, votes_a=votes_a, votes_b=votes_b)


class Command(BaseCommand):
    help = "Populate the database with a rich demo dataset across 10 categories."

    def handle(self, *args, **options):
        # ================= CARS =================
        cars, cs_names, cs = make_category("Cars", "cars", "bi-car-front-fill", "", [
            ("Price (₦m)", "m", False), ("Horsepower", "hp", True),
            ("0-100 km/h", "sec", False), ("Fuel economy", "km/l", True),
        ])
        car_rows = [
            ("Toyota Camry 2025", "Toyota", 45000000, 88, "camry2025", "toyota.com",
             "Reliable midsize sedan with strong resale value.",
             ["Excellent resale value", "Spacious, comfortable cabin", "Toyota reliability reputation"],
             ["Conservative styling", "Infotainment feels dated"], (45, 203, 8.4, 14.5)),
            ("Honda Accord 2025", "Honda", 47000000, 86, "accord2025", "honda.com",
             "Sportier midsize sedan with a refined cabin.",
             ["Sportier handling than most rivals", "Refined, quiet cabin", "Strong safety ratings"],
             ["Pricier than the Camry", "Fewer service centers in some cities"], (47, 192, 8.1, 15.2)),
            ("Toyota Corolla 2025", "Toyota", 28000000, 84, "corolla2025", "toyota.com",
             "Compact, dependable, and cheap to maintain.",
             ["Very affordable to maintain", "Great fuel economy", "Easy to find spare parts"],
             ["Less powerful than midsize rivals", "Firm ride on rough roads"], (28, 169, 9.2, 17.8)),
            ("Hyundai Elantra 2025", "Hyundai", 26000000, 79, "elantra2025", "hyundai.com",
             "Sharp-looking compact sedan loaded with tech.",
             ["Sharp modern design", "Generous warranty", "Loaded with tech for the price"],
             ["Resale value trails Toyota/Honda", "Road noise at highway speed"], (26, 147, 9.8, 16.9)),
            ("Kia K5 2025", "Kia", 32000000, 81, "k52025", "kia.com",
             "Bold styling with a well-equipped interior.",
             ["Bold styling stands out", "Strong base engine power", "Well-equipped interior"],
             ["Fewer dealerships nationwide", "Infotainment lag reported"], (32, 180, 8.6, 15.5)),
            ("Volkswagen Passat 2025", "Volkswagen", 38000000, 78, "passat2025", "volkswagen.com",
             "A comfortable, European-feeling cruiser.",
             ["Solid, European driving feel", "Spacious boot", "Comfortable on long drives"],
             ["Parts can be pricier to source", "Fewer VW specialists locally"], (38, 174, 8.9, 14.9)),
            ("BMW 3 Series 2025", "BMW", 55000000, 90, "bmw3series", "bmw.com",
             "The benchmark sports sedan.",
             ["Excellent driving dynamics", "Premium cabin materials", "Strong brand prestige"],
             ["Costly maintenance", "Run-flat tyres ride firm"], (55, 255, 5.8, 12.8)),
            ("Mercedes-Benz C-Class 2025", "Mercedes-Benz", 58000000, 89, "mercedescclass", "mercedes-benz.com",
             "Effortless comfort with a tech-forward cabin.",
             ["Plush ride comfort", "Standout interior tech", "Strong resale in luxury segment"],
             ["Expensive parts and servicing", "Options add up fast"], (58, 255, 6.0, 12.5)),
            ("Ford Mustang 2025", "Ford", 42000000, 87, "fordmustang", "ford.com",
             "An affordable taste of muscle-car performance.",
             ["Thrilling V8 soundtrack", "Head-turning styling", "Strong straight-line performance"],
             ["Thirsty at the pump", "Cramped rear seats"], (42, 315, 5.3, 10.5)),
            ("Nissan Altima 2025", "Nissan", 27000000, 77, "nissanaltima", "nissan-global.com",
             "A comfortable, no-fuss family sedan.",
             ["Comfortable ride quality", "Roomy cabin", "Competitive pricing"],
             ["CVT gearbox feels uninspiring", "Fewer tech features than rivals"], (27, 188, 8.8, 15.9)),
            ("Chevrolet Malibu 2025", "Chevrolet", 25000000, 74, "chevymalibu", "chevrolet.com",
             "A value-focused midsize sedan.",
             ["Competitive base price", "Decent standard equipment", "Comfortable highway cruiser"],
             ["Fewer dealerships in some regions", "Less engaging to drive"], (25, 160, 9.5, 16.5)),
            ("Peugeot 408 2025", "Peugeot", 30000000, 78, "peugeot408", "peugeot.com",
             "Distinctive styling, popular across West Africa.",
             ["Striking, unusual design", "Comfortable ride", "Well-known local service network"],
             ["Compact-for-the-price rear cabin", "Infotainment menus take getting used to"], (30, 178, 8.9, 16.0)),
            ("Lexus ES 2025", "Lexus", 62000000, 91, "lexuses2025", "lexus.com",
             "A quiet, plush, and dependable luxury sedan.",
             ["Whisper-quiet cabin", "Toyota-level reliability in a luxury package", "Excellent resale value"],
             ["Conservative driving feel", "Premium price"], (62, 302, 6.6, 13.2)),
            ("Mazda 6 2025", "Mazda", 29000000, 80, "mazda6", "mazda.com",
             "An upscale-feeling sedan at a mainstream price.",
             ["Handsome, understated design", "Engaging handling for the class", "Upscale-feeling cabin"],
             ["Smaller rear seat and boot than rivals", "Fewer dealers than bigger brands"], (29, 187, 8.2, 16.8)),
            ("Audi A4 2025", "Audi", 52000000, 86, "audia4", "audi.com",
             "A tech-forward sports sedan.",
             ["Excellent digital cockpit", "Confident all-weather grip (quattro)", "Understated, ages-well design"],
             ["Costly options list", "Firm ride on larger wheels"], (52, 201, 7.3, 13.6)),
            ("Renault Megane 2025", "Renault", 24000000, 73, "renaultmegane", "renault.com",
             "A well-priced, comfortable European hatch-sedan.",
             ["Attractive pricing", "Comfortable ride", "Distinctive French styling"],
             ["Resale value trails Japanese/Korean rivals", "Parts availability varies by region"], (24, 140, 9.9, 17.2)),
        ]
        car_items = build_items(cars, cs_names, cs, car_rows)
        link(cars, car_items["Toyota Camry 2025"], car_items["Honda Accord 2025"], 142, 88, 54)
        link(cars, car_items["Toyota Corolla 2025"], car_items["Hyundai Elantra 2025"], 97, 50, 47)
        link(cars, car_items["BMW 3 Series 2025"], car_items["Mercedes-Benz C-Class 2025"], 156, 80, 60)

        # ================= SMARTPHONES =================
        phones, ph_names, ps = make_category("Smartphones", "smartphones", "bi-phone-fill", "", [
            ("Price (₦)", "", False), ("RAM", "GB", True), ("Battery", "mAh", True),
            ("Camera", "MP", True), ("Storage", "GB", True),
        ])
        phone_rows = [
            ("iPhone 16", "Apple", 1200000, 91, "iphone16", "apple.com",
             "Apple's flagship with the A18 chip.",
             ["Best-in-class chip performance", "Long software update support", "Seamless Apple ecosystem"],
             ["Most expensive option here", "Charger not included"], (1200000, 8, 3561, 48, 256)),
            ("Samsung Galaxy S25", "Samsung", 1100000, 90, "galaxys25", "samsung.com",
             "Samsung's flagship with a big AMOLED screen.",
             ["Big vivid AMOLED display", "More RAM for multitasking", "Versatile camera system"],
             ["One UI has some bloat", "Battery life is good, not great"], (1100000, 12, 4000, 50, 256)),
            ("Google Pixel 9", "Google", 950000, 87, "pixel9", "google.com",
             "Clean Android with excellent computational photography.",
             ["Cleanest Android experience", "Excellent computational photography", "Fast, useful AI features"],
             ["Storage tiers fill up fast", "Availability limited in some regions"], (950000, 12, 4700, 50, 128)),
            ("Xiaomi 14", "Xiaomi", 850000, 85, "xiaomi14", "mi.com",
             "Flagship specs at a friendlier price.",
             ["Flagship specs at a lower price", "Fast charging speed", "Great display for the price"],
             ["HyperOS has a learning curve", "Software updates lag Samsung/Apple"], (850000, 12, 4610, 50, 256)),
            ("Tecno Phantom X2", "Tecno", 550000, 79, "tecnophantomx2", "tecno-mobile.com",
             "Strong specs for the price, popular locally.",
             ["Very affordable for the spec sheet", "Huge battery, lasts all day", "Strong local support network"],
             ["Camera software less polished", "Resale value lower than global brands"], (550000, 8, 5160, 64, 256)),
            ("Infinix Zero 30", "Infinix", 380000, 76, "infinixzero30", "infinixmobility.com",
             "High megapixel camera on a budget.",
             ["High megapixel camera for the price", "Good battery life", "Budget-friendly"],
             ["Build quality feels less premium", "Software has more ads/bloat"], (380000, 8, 5000, 108, 256)),
        ]
        phone_items = build_items(phones, ph_names, ps, phone_rows)
        link(phones, phone_items["iPhone 16"], phone_items["Samsung Galaxy S25"], 210, 130, 80)
        link(phones, phone_items["Tecno Phantom X2"], phone_items["Infinix Zero 30"], 76, 40, 36)

        # ================= FOODS =================
        foods, fo_names, fs = make_category("Foods", "foods", "bi-egg-fried", "", [
            ("Calories", "kcal", False), ("Protein", "g", True),
            ("Price (₦)", "", False), ("Prep time", "mins", False),
        ])
        food_rows = [
            ("Jollof Rice", "West African", 1500, 93, "jollofrice", None,
             "The iconic West African party rice.",
             ["Iconic, crowd-pleasing flavor", "Pairs with almost any protein", "Easy to make in large batches"],
             ["High in carbs if eating light", "Can dry out if reheated poorly"], (620, 14, 1500, 45)),
            ("Fried Rice", "West African", 1600, 85, "friedricenaija", None,
             "A colorful, vegetable-packed rice dish.",
             ["Colorful mix of vegetables", "Slightly lighter than Jollof", "Great for using up leftovers"],
             ["Needs several veggies to taste right", "Less iconic than Jollof at parties"], (580, 13, 1600, 40)),
            ("Pounded Yam & Egusi", "Yoruba cuisine", 2000, 88, "poundedyamegusi", None,
             "A filling classic pairing swallow with melon-seed soup.",
             ["Very filling, keeps you full longer", "Egusi is rich in protein and fat", "Deep, savory flavor"],
             ["Pounding yam by hand is tiring", "Longer prep time than rice dishes"], (710, 22, 2000, 60)),
            ("Amala & Ewedu", "Yoruba cuisine", 1200, 82, "amalaewedu", None,
             "A lighter everyday swallow with a fibrous soup.",
             ["Lower calorie, lighter meal option", "Ewedu is rich in fiber", "Affordable everyday meal"],
             ["Dark color puts some first-timers off", "Best eaten fresh and hot"], (480, 11, 1200, 35)),
            ("Suya", "Northern Nigerian", 1000, 90, "suyanaija", None,
             "Spicy grilled skewers, a Nigerian favorite.",
             ["High protein, great post-workout snack", "Bold spicy flavor", "Quick to prepare/grill"],
             ["Very spicy for some palates", "Street versions vary in hygiene"], (350, 28, 1000, 25)),
            ("Moi Moi", "West African", 800, 80, "moimoinaija", None,
             "Steamed bean pudding, a vegetarian favorite.",
             ["Good vegetarian protein source", "Steams well for meal prep", "Freezes and reheats nicely"],
             ["Bland without the right seasoning mix", "Takes longer to steam through"], (260, 16, 800, 50)),
        ]
        food_items = build_items(foods, fo_names, fs, food_rows)
        link(foods, food_items["Jollof Rice"], food_items["Fried Rice"], 305, 240, 65)
        link(foods, food_items["Suya"], food_items["Moi Moi"], 88, 55, 33)

        # ================= COMPANIES =================
        companies, co_names, cos = make_category(
            "Companies", "companies", "bi-building",
            "Revenue, headcount, and rating figures below are illustrative placeholders for demo purposes, not verified financial data — replace with sourced figures before this category goes live.",
            [("Revenue ($bn)", "bn", True), ("Employees", "", True), ("Customer rating", "/5", True)])
        company_rows = [
            ("Apple", "Big Tech", None, 95, None, "apple.com", "Consumer electronics and services giant.",
             ["Extremely strong brand loyalty", "Tight hardware-software integration", "Massive services revenue"],
             ["Premium pricing limits reach in price-sensitive markets", "Slower to open up its ecosystem"], (391, 164000, 4.5)),
            ("Google", "Big Tech", None, 92, None, "google.com", "Search, advertising, and AI research leader.",
             ["Dominant search and advertising business", "Strong AI research output", "Free tools used by billions"],
             ["Heavy reliance on ad revenue", "History of discontinuing products"], (307, 182000, 4.3)),
            ("Microsoft", "Big Tech", None, 93, None, "microsoft.com", "Enterprise software and cloud computing leader.",
             ["Dominant in enterprise software", "Strong cloud (Azure) growth", "Diversified revenue streams"],
             ["Consumer hardware is a smaller focus", "Windows updates draw regular criticism"], (245, 221000, 4.4)),
            ("Amazon", "Big Tech", None, 90, None, "amazon.com", "E-commerce and cloud infrastructure giant.",
             ["Unmatched logistics and delivery speed", "AWS leads the cloud market", "Huge product selection"],
             ["Warehouse labor practices draw scrutiny", "Thin retail margins"], (574, 1500000, 4.1)),
            ("MTN Group", "Telecom", None, 74, None, "mtn.com", "Africa's largest mobile network operator.",
             ["Widest mobile network coverage in Nigeria", "Strong mobile money (MoMo) growth", "Major regional job creator"],
             ["Currency exposure hits reported earnings", "Customer service complaints are common"], (12, 19000, 3.6)),
            ("Dangote Group", "Conglomerate", None, 77, None, "dangote.com", "West Africa's largest industrial conglomerate.",
             ["Africa's largest cement producer", "New refinery boosts fuel self-sufficiency", "Diversified across cement, sugar, fuel"],
             ["Heavily tied to Nigerian economic conditions", "Founder-dependent leadership structure"], (4.1, 30000, 3.8)),
        ]
        company_items = build_items(companies, co_names, cos, company_rows)
        link(companies, company_items["Apple"], company_items["Google"], 180, 95, 85)
        link(companies, company_items["MTN Group"], company_items["Dangote Group"], 64, 30, 34)

        # ================= TELECOM COMPANIES (global) =================
        telecom, tc_names, ts = make_category(
            "Telecom Companies", "telecom",
            "bi-broadcast-pin",
            "A global spread of mobile network operators. \"Brand\" here shows each company's home region. Revenue/subscriber figures are illustrative placeholders — verify before publishing.",
            [("Revenue ($bn)", "bn", True), ("Subscribers (M)", "M", True),
             ("Countries", "", True), ("Customer Rating", "/5", True)])
        telecom_rows = [
            ("MTN Group", "Africa", None, 78, None, "mtn.com", "Africa's largest mobile network, strong across West and Southern Africa.",
             ["Widest coverage across Africa", "Pioneering mobile money (MoMo)", "Strong brand recognition locally"],
             ["Naira/currency swings hurt reported earnings", "Network quality varies by region"], (12, 290, 19, 3.6)),
            ("Airtel Africa", "Africa", None, 74, None, "airtel.africa", "Fast-growing pan-African operator.",
             ["Competitive data pricing", "Growing mobile money business", "Strong rural coverage push"],
             ["Smaller scale than MTN in some markets", "Customer service complaints common"], (5, 165, 14, 3.5)),
            ("Vodafone", "Europe", None, 82, None, "vodafone.com", "One of Europe's largest telecom groups.",
             ["Broad European footprint", "Strong enterprise/IoT business", "Long-standing brand trust"],
             ["Faces intense low-cost competition", "Complex multi-country structure"], (47, 300, 15, 3.8)),
            ("Deutsche Telekom", "Europe", None, 85, None, "telekom.com", "Germany's leading telecom, owns a majority stake in T-Mobile US.",
             ["Strong home-market network quality", "T-Mobile US stake adds growth", "Heavy fiber/5G investment"],
             ["High capital spending needs", "Regulatory scrutiny in the EU"], (130, 250, 10, 3.9)),
            ("Verizon", "North America", None, 84, None, "verizon.com", "A leading US wireless and broadband carrier.",
             ["Strong US network reliability ratings", "Large enterprise/5G business", "Extensive fiber footprint"],
             ["Premium pricing versus rivals", "Slower growth in a saturated market"], (137, 145, 1, 3.7)),
            ("AT&T", "North America", None, 82, None, "att.com", "One of the largest US telecom carriers.",
             ["Large fiber broadband push", "Bundled wireless/home internet", "Extensive US coverage"],
             ["History of customer service complaints", "Heavy long-term debt load"], (122, 240, 1, 3.6)),
            ("China Mobile", "Asia", None, 88, None, "chinamobileltd.com", "The world's largest mobile operator by subscribers.",
             ["Enormous subscriber base", "Fast nationwide 5G rollout", "State-backed scale and stability"],
             ["Limited presence outside China", "Growth tied closely to domestic policy"], (130, 1000, 1, 4.0)),
            ("Reliance Jio", "Asia", None, 86, None, "jio.com", "The operator that transformed India's data market.",
             ["Very low-cost data plans", "Rapid subscriber growth", "Bundled digital services (JioCinema, etc.)"],
             ["Thin margins per subscriber", "Heavy reliance on the Indian market"], (12, 470, 1, 4.1)),
        ]
        telecom_items = build_items(telecom, tc_names, ts, telecom_rows)
        link(telecom, telecom_items["MTN Group"], telecom_items["Airtel Africa"], 120, 70, 45)
        link(telecom, telecom_items["Verizon"], telecom_items["AT&T"], 95, 50, 40)

        # ================= CONSTRUCTION COMPANIES =================
        construction, cn_names, cns = make_category(
            "Construction Companies", "construction", "bi-buildings",
            "Revenue, headcount, and rating figures are illustrative placeholders — verify before publishing.",
            [("Revenue ($bn)", "bn", True), ("Employees", "", True),
             ("Countries", "", True), ("Industry Rating", "/5", True)])
        construction_rows = [
            ("Julius Berger Nigeria", "Nigeria", None, 80, None, "juliusberger.com",
             "Nigeria's best-known construction and engineering firm.",
             ["Deep experience with major Nigerian infrastructure", "Strong reputation for project quality", "Long local track record"],
             ["Smaller global scale than international rivals", "Heavily tied to Nigerian public contracts"], (1.1, 15000, 3, 3.9)),
            ("China State Construction Engineering", "China", None, 88, None, "cscec.com",
             "One of the world's largest construction companies by revenue.",
             ["Massive global scale", "Fast project delivery timelines", "Deep state-backed financing access"],
             ["Quality concerns raised on some overseas projects", "Less brand recognition in the West"], (240, 380000, 100, 3.7)),
            ("Vinci", "France", None, 89, None, "vinci.com",
             "A diversified French construction and concessions group.",
             ["Diversified across construction, energy, concessions", "Strong European infrastructure track record", "Consistent profitability"],
             ["Complex, sprawling corporate structure", "Exposure to European economic cycles"], (71, 280000, 120, 4.0)),
            ("Bechtel", "USA", None, 85, None, "bechtel.com",
             "A major US engineering, construction, and project management firm.",
             ["Strong reputation on large-scale megaprojects", "Deep US government contract relationships", "Broad energy/infrastructure expertise"],
             ["Some large projects have faced cost overruns", "Less consumer brand recognition"], (20, 55000, 40, 3.9)),
            ("Larsen & Toubro", "India", None, 83, None, "larsentoubro.com",
             "India's largest engineering and construction conglomerate.",
             ["Dominant position in Indian infrastructure", "Diversified into defense and tech", "Strong long-term order book"],
             ["Heavily tied to Indian government spending cycles", "Smaller international footprint than Chinese rivals"], (27, 60000, 50, 3.8)),
            ("Hochtief", "Germany", None, 82, None, "hochtief.de",
             "A major German construction group with global operations.",
             ["Strong European engineering reputation", "Significant presence in Americas via subsidiaries", "Diversified project portfolio"],
             ["Thin margins typical of the industry", "Exposure to currency fluctuations"], (30, 30000, 40, 3.8)),
        ]
        construction_items = build_items(construction, cn_names, cns, construction_rows)
        link(construction, construction_items["Julius Berger Nigeria"], construction_items["China State Construction Engineering"], 58, 35, 20)

        # ================= ELECTRONICS (across types) =================
        electronics, el_names, els = make_category(
            "Electronics", "electronics", "bi-tv-fill",
            "Spans several electronics types (TVs, laptops, appliances, audio, wearables) side by side using a shared, generic spec set.",
            [("Price (₦)", "", False), ("Warranty (yrs)", "yrs", True),
             ("Customer Rating", "/5", True), ("Power Usage (W)", "W", False)])
        electronics_rows = [
            ("Samsung Neo QLED 65\" TV", "Samsung", 1800000, 90, "samsungqled65", "samsung.com",
             "A premium Mini-LED TV with vivid contrast.",
             ["Excellent brightness and contrast", "Great for bright rooms", "Strong smart TV software"],
             ["Premium price for the size", "Some blooming in very dark scenes"], (1800000, 2, 4.6, 150)),
            ("LG OLED55 TV", "LG", 1600000, 91, "lgoled55", "lg.com",
             "A benchmark OLED TV for perfect blacks.",
             ["Perfect black levels", "Excellent for movies and gaming", "Wide viewing angles"],
             ["Risk of burn-in with static images over years", "Not as bright as top Mini-LED sets"], (1600000, 2, 4.7, 120)),
            ("Dell XPS 15 Laptop", "Dell", 1400000, 87, "dellxps15", "dell.com",
             "A premium Windows laptop for creative work.",
             ["Sharp, color-accurate display", "Strong build quality", "Solid performance for creative apps"],
             ["Battery life trails some rivals", "Runs warm under heavy load"], (1400000, 1, 4.4, 65)),
            ("HP Pavilion Laptop", "HP", 650000, 78, "hppavilion", "hp.com",
             "A budget-friendly everyday laptop.",
             ["Affordable for everyday use", "Decent battery life", "Widely available service"],
             ["Build quality feels less premium", "Struggles with heavier workloads"], (650000, 1, 4.1, 45)),
            ("LG InstaView Refrigerator", "LG", 950000, 85, "lgfridge", "lg.com",
             "A smart fridge with a knock-to-see glass panel.",
             ["Knock-to-view panel cuts open-door time", "Spacious interior layout", "Energy-efficient for its size"],
             ["Higher upfront cost than basic fridges", "Smart features need decent home Wi-Fi"], (950000, 5, 4.3, 90)),
            ("Hisense 1.5HP Air Conditioner", "Hisense", 320000, 76, "hisenseac", "hisense.com",
             "An affordable split-unit AC for average-size rooms.",
             ["Affordable upfront cost", "Cools quickly", "Widely available parts/service in Nigeria"],
             ["Louder than premium inverter units", "Less energy-efficient than top-tier brands"], (320000, 2, 4.0, 1100)),
            ("Sony WH-1000XM5 Headphones", "Sony", 450000, 93, "sonywh1000xm5", "sony.com",
             "Class-leading noise-cancelling headphones.",
             ["Excellent noise cancellation", "All-day comfort", "Strong battery life"],
             ["Premium price point", "Case is bulkier than some rivals"], (450000, 1, 4.8, 2)),
            ("Apple Watch Series 10", "Apple", 550000, 89, "applewatch10", "apple.com",
             "A polished smartwatch tightly tied to the iPhone.",
             ["Best-in-class app/accessory ecosystem", "Reliable health tracking", "Fast charging"],
             ["Battery life trails some Android rivals", "Best features require an iPhone"], (550000, 1, 4.5, 1)),
        ]
        electronics_items = build_items(electronics, el_names, els, electronics_rows)
        link(electronics, electronics_items["Samsung Neo QLED 65\" TV"], electronics_items["LG OLED55 TV"], 140, 75, 55)
        link(electronics, electronics_items["Dell XPS 15 Laptop"], electronics_items["HP Pavilion Laptop"], 90, 60, 25)

        # ================= FOOTBALLERS (by achievements) =================
        # Stats checked against live search in early July 2026 (mid-World-Cup) where
        # possible, but goal tallies especially will already be stale by the time you
        # read this -- they update almost daily during an active tournament. Ballon d'Or
        # counts are stable (awarded once a year); everything else, verify before publishing.
        footballers, fb_names, fbs = make_category(
            "Footballers", "footballers", "bi-person-fill",
            "Compared by career achievements, not live match stats. No photos are used — see README for why — just initials. Figures are approximate as of July 2026 and will date quickly, especially mid-World-Cup.",
            [("Ballon d'Or Awards", "", True), ("Career Goals", "", True),
             ("International Goals", "", True), ("Champions League Titles", "", True)])
        footballer_rows = [
            ("Lionel Messi", "Inter Miami", None, 98, None, None,
             "Argentine forward, widely regarded as one of the greatest players ever.",
             ["Record 8 Ballon d'Or awards", "All-time World Cup top scorer", "Won the World Cup with Argentina in 2022"],
             ["Fewer major trophies since leaving Europe", "Now past his peak physical pace"], (8, 917, 124, 4)),
            ("Cristiano Ronaldo", "Al Nassr", None, 97, None, None,
             "Portuguese forward, closing in on 1,000 career goals.",
             ["All-time men's international top scorer", "5 Champions League titles", "Remarkable longevity into his 40s"],
             ["Never won a World Cup", "No Ballon d'Or since 2017"], (5, 976, 146, 5)),
            ("Kylian Mbappé", "Real Madrid", None, 93, None, None,
             "French forward, World Cup winner at just 19.",
             ["World Cup winner in 2018 at age 19", "Multiple Ligue 1 top-scorer titles", "Among the fastest players in the world"],
             ["No Ballon d'Or win yet", "Still building his Champions League trophy haul at Real Madrid"], (0, 320, 48, 0)),
            ("Erling Haaland", "Manchester City", None, 92, None, None,
             "Norwegian striker with a remarkable goals-per-game record.",
             ["Broke the Premier League single-season goals record", "Won the Champions League with Man City in 2023", "Exceptional goals-per-90 ratio"],
             ["No Ballon d'Or win yet", "Limited international trophy chances with Norway"], (0, 320, 40, 1)),
            ("Victor Osimhen", "Galatasaray", None, 85, None, None,
             "Nigerian striker, 2023 CAF Player of the Year.",
             ["2023 CAF (African) Player of the Year", "Serie A top scorer with Napoli", "Nigeria's all-time UEFA Champions League scorer"],
             ["No Ballon d'Or win yet", "Yet to win a Champions League title"], (0, 200, 26, 0)),
            ("Mohamed Salah", "Liverpool", None, 94, None, None,
             "Egyptian forward, Liverpool's modern-day record scorer.",
             ["Multiple Premier League Golden Boots", "Won the Champions League with Liverpool in 2019", "Egypt's all-time leading scorer"],
             ["No Ballon d'Or win yet", "International trophies have been elusive with Egypt"], (0, 260, 55, 1)),
        ]
        footballer_items = build_items(footballers, fb_names, fbs, footballer_rows)
        link(footballers, footballer_items["Lionel Messi"], footballer_items["Cristiano Ronaldo"], 520, 290, 210)
        link(footballers, footballer_items["Victor Osimhen"], footballer_items["Mohamed Salah"], 110, 55, 50)

        # ================= UNIVERSITIES (top global) =================
        universities, un_names, uns = make_category(
            "Universities", "universities", "bi-mortarboard-fill",
            "Ranking is from the QS World University Rankings 2026. Acceptance rate, tuition, and Nobel counts are approximate — verify current figures before publishing.",
            [("World Ranking (QS 2026)", "", False), ("Acceptance Rate", "%", False),
             ("Tuition ($k/yr)", "$k", False), ("Nobel Laureates", "", True)])
        university_rows = [
            ("MIT", "USA", None, 99, "mitcampus", "mit.edu",
             "Ranked #1 in the world for the 14th straight year (QS 2026).",
             ["World's #1 ranked university (QS 2026)", "Legendary strength in engineering and CS", "Huge alumni startup/research footprint"],
             ["Extremely low acceptance rate", "High cost of attendance"], (1, 4, 60, 100)),
            ("Imperial College London", "UK", None, 95, "imperialcampus", "imperial.ac.uk",
             "Climbed to #2 globally in the QS 2026 rankings.",
             ["Rose sharply in the latest world rankings", "Strong STEM and medicine focus", "Central London location"],
             ["Narrower subject breadth than large US universities", "High cost of living in London"], (2, 11, 45, 14)),
            ("Stanford University", "USA", None, 97, "stanfordcampus", "stanford.edu",
             "A powerhouse for tech, business, and research.",
             ["Deep Silicon Valley connections", "Excellent interdisciplinary research funding", "Strong entrepreneurship culture"],
             ["Very low acceptance rate", "High tuition and cost of living"], (3, 4, 62, 85)),
            ("University of Oxford", "UK", None, 96, "oxfordcampus", "ox.ac.uk",
             "One of the world's oldest and most prestigious universities.",
             ["Centuries of academic prestige", "Tutorial-based teaching model", "Strong humanities and sciences alike"],
             ["Selective and interview-intensive admissions", "Collegiate system can feel fragmented"], (4, 17, 40, 72)),
            ("Harvard University", "USA", None, 98, "harvardcampus", "harvard.edu",
             "The most Nobel-laureate-affiliated university in the world.",
             ["Largest university endowment globally", "Enormous alumni network", "Most Nobel laureates of any university"],
             ["Extremely low acceptance rate", "High sticker-price tuition"], (5, 3, 58, 161)),
            ("University of Cambridge", "UK", None, 95, "cambridgecampus", "cam.ac.uk",
             "A historic rival to Oxford, strong across sciences.",
             ["Exceptional record in the sciences", "Historic, globally recognized prestige", "Strong research output per capita"],
             ["Selective and interview-intensive admissions", "Cold, competitive academic pace"], (6, 21, 42, 120)),
        ]
        university_items = build_items(universities, un_names, uns, university_rows)
        link(universities, university_items["MIT"], university_items["Stanford University"], 88, 45, 40)
        link(universities, university_items["Harvard University"], university_items["University of Oxford"], 76, 38, 35)

        # ================= CLOTHING BRANDS =================
        clothing, cl_names, cls = make_category(
            "Clothing Brands", "clothing", "bi-bag-fill",
            "Revenue, headcount, and rating figures are illustrative placeholders — verify before publishing.",
            [("Revenue ($bn)", "bn", True), ("Employees", "", True), ("Customer Rating", "/5", True)])
        clothing_rows = [
            ("Nike", "USA", None, 92, None, "nike.com", "The world's largest sportswear brand by revenue.",
             ["Unmatched global brand recognition", "Deep roster of athlete endorsements", "Strong innovation in footwear tech"],
             ["Premium pricing versus rivals", "Heavy reliance on North American market"], (51, 79000, 4.3)),
            ("Adidas", "Germany", None, 89, None, "adidas.com", "A global sportswear leader known for its three stripes.",
             ["Strong football/soccer heritage", "Successful lifestyle collabs (e.g. Originals)", "Broad global manufacturing footprint"],
             ["Trails Nike in North American market share", "Past reliance on single-partner collabs caused volatility"], (24, 61000, 4.2)),
            ("Puma", "Germany", None, 82, None, "puma.com", "A sportswear brand strong in football and motorsport.",
             ["Strong football and motorsport sponsorships", "Competitive pricing versus the top two", "Growing lifestyle/fashion collabs"],
             ["Smaller marketing budget than Nike/Adidas", "Less market share in North America"], (8.8, 20000, 4.0)),
            ("Under Armour", "USA", None, 76, None, "underarmour.com", "A performance-apparel brand built on moisture-wicking gear.",
             ["Strong reputation in performance base-layers", "Popular with American college/pro athletes", "Focused brand identity"],
             ["Smaller global footprint than Nike/Adidas", "Revenue growth has been inconsistent"], (5.3, 14000, 3.8)),
            ("New Balance", "USA", None, 85, None, "newbalance.com", "An independent, US-manufacturing-focused sneaker brand.",
             ["Strong 'made in USA/UK' manufacturing story", "Cult favorite in sneaker culture", "Independently owned, family-run"],
             ["Smaller global marketing reach", "Less presence in team sports sponsorship"], (7.8, 8000, 4.3)),
            ("Reebok", "USA", None, 74, None, "reebok.com", "A fitness-heritage brand now owned by Authentic Brands Group.",
             ["Strong CrossFit/fitness heritage", "Recognizable retro sneaker lines", "Competitive pricing"],
             ["Lost significant market share since the 2000s", "Less cultural relevance than peak years"], (2.5, 5000, 3.9)),
        ]
        clothing_items = build_items(clothing, cl_names, cls, clothing_rows)
        link(clothing, clothing_items["Nike"], clothing_items["Adidas"], 180, 100, 72)

        total_items = (len(car_items) + len(phone_items) + len(food_items) + len(company_items)
                       + len(telecom_items) + len(construction_items) + len(electronics_items)
                       + len(footballer_items) + len(university_items) + len(clothing_items))
        self.stdout.write(self.style.SUCCESS(
            f"Seeded 10 categories, {total_items} items, full specs, reviews, logos, and popular comparisons."
        ))
