class BaseScraper:
    name: str
    supported_types: list = []  # Ex: ["NAME", "CPF", "EMAIL"]
    
    def search(self, intent: dict) -> list:
        raise NotImplementedError
