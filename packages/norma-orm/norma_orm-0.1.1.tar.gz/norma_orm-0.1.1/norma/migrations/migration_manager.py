"""
Norma Migration Manager

Handles database migrations for schema changes.
"""

import os
import json
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

from ..core.base_model import BaseModel
from ..exceptions import QueryError, ConfigurationError


@dataclass
class Migration:
    """Represents a database migration."""
    
    id: str
    name: str
    description: str
    created_at: datetime
    applied_at: Optional[datetime] = None
    up_operations: List[Dict[str, Any]] = None
    down_operations: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.up_operations is None:
            self.up_operations = []
        if self.down_operations is None:
            self.down_operations = []


class MigrationManager:
    """
    Manages database migrations for Norma ORM.
    
    Provides functionality to:
    - Create migrations
    - Apply migrations
    - Rollback migrations
    - Track migration history
    """
    
    def __init__(self, client, migrations_dir: str = "migrations"):
        """
        Initialize migration manager.
        
        Args:
            client: NormaClient instance
            migrations_dir: Directory to store migration files
        """
        self.client = client
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Create migrations table if it doesn't exist
        self._migration_table_created = False
    
    async def _ensure_migration_table(self):
        """Ensure the migrations tracking table exists."""
        if self._migration_table_created:
            return
        
        # Create a simple migration tracking table
        # This is adapter-specific implementation
        adapter = self.client.adapter
        
        if hasattr(adapter, 'session') or hasattr(adapter, '_engine'):
            # SQL adapter
            await self._create_sql_migration_table()
        elif hasattr(adapter, 'database'):
            # MongoDB adapter
            await self._create_mongo_migration_collection()
        elif hasattr(adapter, 'session') and hasattr(adapter, 'keyspace'):
            # Cassandra adapter
            await self._create_cassandra_migration_table()
        
        self._migration_table_created = True
    
    async def _create_sql_migration_table(self):
        """Create migration table for SQL databases."""
        try:
            if self.client.adapter._async_engine:
                async with self.client.adapter._async_session_factory() as session:
                    await session.execute("""
                        CREATE TABLE IF NOT EXISTS norma_migrations (
                            id VARCHAR(255) PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            created_at TIMESTAMP NOT NULL,
                            applied_at TIMESTAMP
                        )
                    """)
                    await session.commit()
        except Exception as e:
            raise QueryError(f"Failed to create migration table: {str(e)}")
    
    async def _create_mongo_migration_collection(self):
        """Create migration collection for MongoDB."""
        # MongoDB doesn't require explicit collection creation
        pass
    
    async def _create_cassandra_migration_table(self):
        """Create migration table for Cassandra."""
        try:
            create_table_cql = """
            CREATE TABLE IF NOT EXISTS norma_migrations (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                created_at TIMESTAMP,
                applied_at TIMESTAMP
            )
            """
            self.client.adapter.session.execute(create_table_cql)
        except Exception as e:
            raise QueryError(f"Failed to create migration table: {str(e)}")
    
    def create_migration(self, name: str, description: str = "") -> Migration:
        """
        Create a new migration file.
        
        Args:
            name: Migration name
            description: Migration description
            
        Returns:
            Created Migration object
        """
        # Generate migration ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_id = f"{timestamp}_{name.lower().replace(' ', '_')}"
        
        migration = Migration(
            id=migration_id,
            name=name,
            description=description,
            created_at=datetime.now()
        )
        
        # Save migration file
        migration_file = self.migrations_dir / f"{migration_id}.json"
        with open(migration_file, 'w') as f:
            json.dump(asdict(migration), f, indent=2, default=str)
        
        return migration
    
    def load_migration(self, migration_id: str) -> Optional[Migration]:
        """Load a migration from file."""
        migration_file = self.migrations_dir / f"{migration_id}.json"
        
        if not migration_file.exists():
            return None
        
        try:
            with open(migration_file, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            if isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data.get('applied_at') and isinstance(data['applied_at'], str):
                data['applied_at'] = datetime.fromisoformat(data['applied_at'])
            
            return Migration(**data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load migration {migration_id}: {str(e)}")
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        all_migrations = self.get_all_migrations()
        return [m for m in all_migrations if m.applied_at is None]
    
    def get_all_migrations(self) -> List[Migration]:
        """Get all migrations sorted by creation time."""
        migrations = []
        
        for migration_file in sorted(self.migrations_dir.glob("*.json")):
            migration_id = migration_file.stem
            migration = self.load_migration(migration_id)
            if migration:
                migrations.append(migration)
        
        return sorted(migrations, key=lambda m: m.created_at)
    
    async def apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration.
        
        Args:
            migration: Migration to apply
            
        Returns:
            True if successful
        """
        await self._ensure_migration_table()
        
        try:
            # Execute up operations
            for operation in migration.up_operations:
                await self._execute_operation(operation)
            
            # Mark as applied
            migration.applied_at = datetime.now()
            await self._record_migration(migration)
            
            # Update migration file
            migration_file = self.migrations_dir / f"{migration.id}.json"
            with open(migration_file, 'w') as f:
                json.dump(asdict(migration), f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            raise QueryError(f"Failed to apply migration {migration.id}: {str(e)}")
    
    async def rollback_migration(self, migration: Migration) -> bool:
        """
        Rollback a single migration.
        
        Args:
            migration: Migration to rollback
            
        Returns:
            True if successful
        """
        await self._ensure_migration_table()
        
        try:
            # Execute down operations
            for operation in migration.down_operations:
                await self._execute_operation(operation)
            
            # Mark as not applied
            migration.applied_at = None
            await self._remove_migration_record(migration)
            
            # Update migration file
            migration_file = self.migrations_dir / f"{migration.id}.json"
            with open(migration_file, 'w') as f:
                json.dump(asdict(migration), f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            raise QueryError(f"Failed to rollback migration {migration.id}: {str(e)}")
    
    async def apply_all_pending(self) -> int:
        """
        Apply all pending migrations.
        
        Returns:
            Number of migrations applied
        """
        pending_migrations = self.get_pending_migrations()
        applied_count = 0
        
        for migration in pending_migrations:
            await self.apply_migration(migration)
            applied_count += 1
        
        return applied_count
    
    async def _execute_operation(self, operation: Dict[str, Any]):
        """Execute a migration operation."""
        op_type = operation.get('type')
        
        if op_type == 'create_table':
            await self._execute_create_table(operation)
        elif op_type == 'drop_table':
            await self._execute_drop_table(operation)
        elif op_type == 'add_column':
            await self._execute_add_column(operation)
        elif op_type == 'drop_column':
            await self._execute_drop_column(operation)
        elif op_type == 'create_index':
            await self._execute_create_index(operation)
        elif op_type == 'drop_index':
            await self._execute_drop_index(operation)
        elif op_type == 'raw_sql':
            await self._execute_raw_sql(operation)
        else:
            raise QueryError(f"Unknown migration operation type: {op_type}")
    
    async def _execute_create_table(self, operation: Dict[str, Any]):
        """Execute create table operation."""
        model_name = operation.get('model_name')
        if not model_name:
            raise QueryError("create_table operation requires model_name")
        
        # This would need model class resolution
        # For now, just log the operation
        pass
    
    async def _execute_drop_table(self, operation: Dict[str, Any]):
        """Execute drop table operation."""
        table_name = operation.get('table_name')
        if not table_name:
            raise QueryError("drop_table operation requires table_name")
        
        # Execute based on adapter type
        adapter = self.client.adapter
        
        if hasattr(adapter, '_engine'):
            # SQL adapter
            if adapter._async_engine:
                async with adapter._async_session_factory() as session:
                    await session.execute(f"DROP TABLE IF EXISTS {table_name}")
                    await session.commit()
    
    async def _execute_add_column(self, operation: Dict[str, Any]):
        """Execute add column operation."""
        # Implementation would depend on adapter type
        pass
    
    async def _execute_drop_column(self, operation: Dict[str, Any]):
        """Execute drop column operation."""
        # Implementation would depend on adapter type
        pass
    
    async def _execute_create_index(self, operation: Dict[str, Any]):
        """Execute create index operation."""
        # Implementation would depend on adapter type
        pass
    
    async def _execute_drop_index(self, operation: Dict[str, Any]):
        """Execute drop index operation."""
        # Implementation would depend on adapter type
        pass
    
    async def _execute_raw_sql(self, operation: Dict[str, Any]):
        """Execute raw SQL operation."""
        sql = operation.get('sql')
        if not sql:
            raise QueryError("raw_sql operation requires sql")
        
        adapter = self.client.adapter
        
        if hasattr(adapter, '_engine'):
            # SQL adapter
            if adapter._async_engine:
                async with adapter._async_session_factory() as session:
                    await session.execute(sql)
                    await session.commit()
    
    async def _record_migration(self, migration: Migration):
        """Record migration as applied."""
        # This would insert into the migrations tracking table
        pass
    
    async def _remove_migration_record(self, migration: Migration):
        """Remove migration record."""
        # This would remove from the migrations tracking table
        pass
