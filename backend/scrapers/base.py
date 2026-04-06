class BaseScraper:
    name: str
    def search(self, intent: dict) -> list:
        raise NotImplementedError
