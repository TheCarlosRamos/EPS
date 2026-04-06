SCRAPERS = {}

def register(scraper):
    SCRAPERS[scraper.name] = scraper

def all_scrapers():
    return SCRAPERS.values()
