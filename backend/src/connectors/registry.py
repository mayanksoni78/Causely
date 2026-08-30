from src.connectors.base import SourceConnector, ConnectorStatus

class ConnectorRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connectors = {}
        return cls._instance

    def register(self, connector_id: str, connector: SourceConnector):
        self._connectors[connector_id] = connector

    def get(self, connector_id: str) -> SourceConnector | None:
        return self._connectors.get(connector_id)

    def list_available(self) -> list[str]:
        return list(self._connectors.keys())

    def health_check_all(self) -> dict[str, ConnectorStatus]:
        return {cid: connector.health_check() for cid, connector in self._connectors.items()}

registry = ConnectorRegistry()
