"""
Norma Relationship Manager

Handles relationship loading and querying between models.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import fields
from collections import defaultdict

from .base_model import BaseModel
from .field import FieldConfig, RelationType
from ..exceptions import QueryError, ValidationError


T = TypeVar('T', bound=BaseModel)


class RelationshipManager:
    """
    Manages relationships between models and provides relationship loading.
    
    Handles:
    - Lazy loading of related models
    - Eager loading with joins
    - Relationship validation
    - Cascade operations
    """
    
    def __init__(self, client):
        """
        Initialize relationship manager.
        
        Args:
            client: NormaClient instance for database operations
        """
        self.client = client
        self._relationship_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    async def load_relationships(
        self, 
        model: T, 
        relationships: Optional[List[str]] = None,
        depth: int = 1
    ) -> T:
        """
        Load relationships for a model instance.
        
        Args:
            model: Model instance to load relationships for
            relationships: Specific relationships to load (None for all)
            depth: Maximum depth for nested relationship loading
            
        Returns:
            Model with loaded relationships
        """
        if depth <= 0:
            return model
        
        model_class = model.__class__
        relationship_fields = model_class.get_relationship_fields()
        
        if not relationship_fields:
            return model
        
        # Filter relationships if specified
        if relationships:
            relationship_fields = {
                k: v for k, v in relationship_fields.items() 
                if k in relationships
            }
        
        # Load each relationship
        for field_name, config in relationship_fields.items():
            if not config.relationship:
                continue
                
            try:
                related_data = await self._load_relationship(
                    model, field_name, config, depth - 1
                )
                setattr(model, f"_{field_name}_loaded", related_data)
            except Exception as e:
                # Log error but don't fail the entire operation
                pass
        
        return model
    
    async def _load_relationship(
        self,
        model: BaseModel,
        field_name: str,
        config: FieldConfig,
        remaining_depth: int
    ) -> Any:
        """Load a specific relationship."""
        relationship = config.relationship
        if not relationship:
            return None
        
        # Get the target model class
        target_model_class = self._resolve_model_class(relationship.target_model)
        if not target_model_class:
            raise QueryError(f"Could not resolve target model: {relationship.target_model}")
        
        # Get the foreign key value
        foreign_key_value = getattr(model, field_name)
        if not foreign_key_value:
            return None
        
        # Load based on relationship type
        if relationship.relation_type == RelationType.ONE_TO_ONE:
            return await self._load_one_to_one(
                target_model_class, relationship, foreign_key_value, remaining_depth
            )
        elif relationship.relation_type == RelationType.MANY_TO_ONE:
            return await self._load_many_to_one(
                target_model_class, relationship, foreign_key_value, remaining_depth
            )
        elif relationship.relation_type == RelationType.ONE_TO_MANY:
            return await self._load_one_to_many(
                target_model_class, relationship, foreign_key_value, remaining_depth
            )
        elif relationship.relation_type == RelationType.MANY_TO_MANY:
            return await self._load_many_to_many(
                target_model_class, relationship, foreign_key_value, remaining_depth
            )
        
        return None
    
    async def _load_one_to_one(
        self,
        target_model_class: Type[BaseModel],
        relationship,
        foreign_key_value: Any,
        remaining_depth: int
    ) -> Optional[BaseModel]:
        """Load one-to-one relationship."""
        target_client = self.client.get_model_client(target_model_class)
        
        # Find the related model
        foreign_key_field = relationship.foreign_key or target_model_class.get_primary_key_field()
        related_model = await target_client.find_by_id(foreign_key_value)
        
        if related_model and remaining_depth > 0:
            related_model = await self.load_relationships(related_model, depth=remaining_depth)
        
        return related_model
    
    async def _load_many_to_one(
        self,
        target_model_class: Type[BaseModel],
        relationship,
        foreign_key_value: Any,
        remaining_depth: int
    ) -> Optional[BaseModel]:
        """Load many-to-one relationship (same as one-to-one)."""
        return await self._load_one_to_one(
            target_model_class, relationship, foreign_key_value, remaining_depth
        )
    
    async def _load_one_to_many(
        self,
        target_model_class: Type[BaseModel],
        relationship,
        foreign_key_value: Any,
        remaining_depth: int
    ) -> List[BaseModel]:
        """Load one-to-many relationship."""
        target_client = self.client.get_model_client(target_model_class)
        
        # Find all related models
        foreign_key_field = relationship.foreign_key or "id"
        filters = {foreign_key_field: foreign_key_value}
        related_models = await target_client.find_many(filters)
        
        # Load nested relationships if needed
        if remaining_depth > 0:
            for i, model in enumerate(related_models):
                related_models[i] = await self.load_relationships(model, depth=remaining_depth)
        
        return related_models
    
    async def _load_many_to_many(
        self,
        target_model_class: Type[BaseModel],
        relationship,
        foreign_key_value: Any,
        remaining_depth: int
    ) -> List[BaseModel]:
        """Load many-to-many relationship."""
        # This is a simplified implementation
        # In a real scenario, you'd need junction tables
        target_client = self.client.get_model_client(target_model_class)
        
        # For now, assume foreign_key_value is a list of IDs
        if not isinstance(foreign_key_value, list):
            return []
        
        related_models = []
        for fk_value in foreign_key_value:
            model = await target_client.find_by_id(fk_value)
            if model:
                if remaining_depth > 0:
                    model = await self.load_relationships(model, depth=remaining_depth)
                related_models.append(model)
        
        return related_models
    
    def _resolve_model_class(self, model_name: str) -> Optional[Type[BaseModel]]:
        """
        Resolve model class by name.
        
        This is a simplified implementation. In a real scenario,
        you'd have a model registry.
        """
        # Try to import from common locations
        import sys
        import importlib
        
        # Check if already imported
        for module_name, module in sys.modules.items():
            if hasattr(module, model_name):
                cls = getattr(module, model_name)
                if isinstance(cls, type) and issubclass(cls, BaseModel):
                    return cls
        
        return None
    
    async def cascade_delete(self, model: BaseModel) -> List[BaseModel]:
        """
        Perform cascade delete operations.
        
        Args:
            model: Model instance being deleted
            
        Returns:
            List of models that were cascade deleted
        """
        deleted_models = []
        model_class = model.__class__
        relationship_fields = model_class.get_relationship_fields()
        
        for field_name, config in relationship_fields.items():
            relationship = config.relationship
            if not relationship or not relationship.cascade_delete:
                continue
            
            try:
                # Load related models
                related_data = await self._load_relationship(model, field_name, config, 0)
                
                if related_data:
                    if isinstance(related_data, list):
                        # One-to-many or many-to-many
                        for related_model in related_data:
                            await self._delete_related_model(related_model)
                            deleted_models.append(related_model)
                    else:
                        # One-to-one or many-to-one
                        await self._delete_related_model(related_data)
                        deleted_models.append(related_data)
                        
            except Exception as e:
                # Log error but continue with other relationships
                pass
        
        return deleted_models
    
    async def _delete_related_model(self, model: BaseModel) -> bool:
        """Delete a related model."""
        model_client = self.client.get_model_client(model.__class__)
        pk_value = model.get_primary_key_value()
        if pk_value:
            return await model_client.delete_by_id(pk_value)
        return False
    
    def clear_cache(self):
        """Clear the relationship cache."""
        self._relationship_cache.clear()


# Convenience functions for relationship queries

async def load_with_relationships(
    client,
    model: T,
    relationships: Optional[List[str]] = None,
    depth: int = 1
) -> T:
    """
    Load a model with its relationships.
    
    Args:
        client: NormaClient instance
        model: Model to load relationships for
        relationships: Specific relationships to load
        depth: Maximum depth for nested loading
        
    Returns:
        Model with loaded relationships
    """
    manager = RelationshipManager(client)
    return await manager.load_relationships(model, relationships, depth)


async def find_with_relationships(
    client,
    model_class: Type[T],
    filters: Optional[Dict[str, Any]] = None,
    relationships: Optional[List[str]] = None,
    depth: int = 1,
    **kwargs
) -> List[T]:
    """
    Find models with their relationships loaded.
    
    Args:
        client: NormaClient instance
        model_class: Model class to query
        filters: Query filters
        relationships: Specific relationships to load
        depth: Maximum depth for nested loading
        **kwargs: Additional query parameters
        
    Returns:
        List of models with loaded relationships
    """
    model_client = client.get_model_client(model_class)
    models = await model_client.find_many(filters, **kwargs)
    
    manager = RelationshipManager(client)
    loaded_models = []
    
    for model in models:
        loaded_model = await manager.load_relationships(model, relationships, depth)
        loaded_models.append(loaded_model)
    
    return loaded_models
