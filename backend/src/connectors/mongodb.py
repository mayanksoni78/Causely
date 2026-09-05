import uuid
import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class MongoDBConnector(SourceConnector):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connector_id = f"mongodb_{uuid.uuid4().hex[:8]}"

    def check_permissions(self) -> PermissionReport:
        warnings = []
        is_read_only = False
        granted_scopes = []
        
        try:
            client = pymongo.MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            # Simple check if we can read collections
            db = client.get_default_database()
            if db.name:
                db.list_collection_names()
                granted_scopes.append("read_collections")
                is_read_only = True
                
        except Exception as e:
            warnings.append(str(e))
            
        return PermissionReport(
            connector_id=self.connector_id,
            is_read_only=is_read_only,
            granted_scopes=granted_scopes,
            warnings=warnings
        )

    def list_capabilities(self) -> list[str]:
        return ["query_documents"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        return []

    def health_check(self) -> ConnectorStatus:
        try:
            client = pymongo.MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            return ConnectorStatus(healthy=True, message="Connected to MongoDB")
        except Exception as e:
            return ConnectorStatus(healthy=False, message=str(e))
