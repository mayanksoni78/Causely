from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk
import json

class PostgresConnector(SourceConnector):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        try:
            self.engine = create_engine(self.connection_string)
        except Exception:
            self.engine = None

    def check_permissions(self) -> PermissionReport:
        if not self.engine:
            return PermissionReport("postgres", False, [], ["Invalid connection string format"])
        
        warnings = []
        try:
            with self.engine.connect() as conn:
                # We can't guarantee a strict read-only user just by checking the engine,
                # but we can do a sanity check. In a real system we'd check pg_roles.
                pass
        except SQLAlchemyError as e:
            return PermissionReport("postgres", False, [], [f"Connection failed: {str(e)}"])
            
        return PermissionReport("postgres", True, ["read_schema", "read_tables"], warnings)

    def list_capabilities(self) -> list[str]:
        return ["schema_discovery", "table_sampling"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        if not self.engine:
            return []
            
        chunks = []
        try:
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            
            # Simple schema representation as chunks
            for table_name, table in metadata.tables.items():
                if query.query_text.lower() in table_name.lower():
                    cols = [f"{c.name} ({c.type})" for c in table.columns]
                    content = f"Table: {table_name}\nColumns: {', '.join(cols)}"
                    
                    chunks.append(EvidenceChunk(
                        id=f"pg_{table_name}",
                        source_id="pg",
                        connector_type="postgres",
                        content=content,
                        metadata={"table": table_name},
                        relevance_score=1.0
                    ))
        except Exception as e:
            print(f"Postgres fetch error: {e}")
            
        return chunks

    def health_check(self) -> ConnectorStatus:
        if not self.engine:
            return ConnectorStatus(False, "Engine not initialized")
        try:
            with self.engine.connect():
                return ConnectorStatus(True, "Connected")
        except SQLAlchemyError as e:
            return ConnectorStatus(False, str(e))
