

class EsIndex:
    def __init(self, url: str, port: int, index_name: str, index_settings: dict):
        self.url = url
        self.port = port
        self.index_name = index_name
        self.index_settings = index_settings

    async def create(self):
        pass

    async def delete(self):
        pass