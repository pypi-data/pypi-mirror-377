"""
Knowledge manager for coordinating multiple knowledge bases.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseKnowledgeBase, KnowledgeQuery, KnowledgeResult, KnowledgeProvider
from .embedchain_adapter import EmbedchainProvider
from ..core.exceptions import KnowledgeError


class KnowledgeManager:
    """
    Central manager for all knowledge bases in a team.
    
    This class coordinates multiple knowledge bases and provides a unified
    interface for querying and managing knowledge across the system.
    """
    
    def __init__(self):
        """Initialize the knowledge manager."""
        self.knowledge_bases: Dict[str, BaseKnowledgeBase] = {}
        self.providers: Dict[str, KnowledgeProvider] = {}
        self.logger = logging.getLogger(__name__)
        
        # Register default providers
        self._register_default_providers()
    
    def _register_default_providers(self) -> None:
        """Register default knowledge providers."""
        try:
            embedchain_provider = EmbedchainProvider()
            self.register_provider('embedchain', embedchain_provider)
            self.logger.debug("Registered Embedchain provider")
        except ImportError:
            self.logger.warning("Embedchain not available, skipping provider registration")
    
    def register_provider(self, name: str, provider: KnowledgeProvider) -> None:
        """
        Register a knowledge provider.
        
        Args:
            name: Provider name
            provider: Provider instance
        """
        self.providers[name] = provider
        self.logger.info(f"Registered knowledge provider: {name}")
    
    def create_knowledge_base(
        self, 
        name: str, 
        kb_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseKnowledgeBase:
        """
        Create a new knowledge base.
        
        Args:
            name: Knowledge base name
            kb_type: Type of knowledge base
            config: Optional configuration
            
        Returns:
            Created knowledge base instance
            
        Raises:
            KnowledgeError: If creation fails
        """
        if name in self.knowledge_bases:
            raise KnowledgeError(f"Knowledge base '{name}' already exists")
        
        # Find a provider that supports this type
        provider = None
        for provider_name, provider_instance in self.providers.items():
            if kb_type in provider_instance.get_supported_types():
                provider = provider_instance
                break
        
        if not provider:
            raise KnowledgeError(f"No provider found for knowledge base type '{kb_type}'")
        
        try:
            kb = provider.create_knowledge_base(name, kb_type, config)
            self.knowledge_bases[name] = kb
            self.logger.info(f"Created knowledge base '{name}' of type '{kb_type}'")
            return kb
        except Exception as e:
            raise KnowledgeError(f"Failed to create knowledge base '{name}': {e}")
    
    def get_knowledge_base(self, name: str) -> Optional[BaseKnowledgeBase]:
        """
        Get a knowledge base by name.
        
        Args:
            name: Knowledge base name
            
        Returns:
            Knowledge base instance or None if not found
        """
        return self.knowledge_bases.get(name)
    
    async def add_data_to_knowledge_base(
        self, 
        kb_name: str, 
        data: str, 
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add data to a knowledge base.
        
        Args:
            kb_name: Knowledge base name
            data: Data to add
            source: Optional source identifier
            metadata: Optional metadata
            
        Raises:
            KnowledgeError: If knowledge base not found or addition fails
        """
        kb = self.get_knowledge_base(kb_name)
        if not kb:
            raise KnowledgeError(f"Knowledge base '{kb_name}' not found")
        
        if not kb.is_initialized():
            await kb.initialize()
        
        try:
            await kb.add_data(data, source or data[:50], metadata)
            self.logger.debug(f"Added data to knowledge base '{kb_name}'")
        except Exception as e:
            raise KnowledgeError(f"Failed to add data to knowledge base '{kb_name}': {e}")
    
    async def query_knowledge_base(
        self, 
        kb_name: str, 
        query: str, 
        max_results: int = 5
    ) -> List[KnowledgeResult]:
        """
        Query a specific knowledge base.
        
        Args:
            kb_name: Knowledge base name
            query: Query string
            max_results: Maximum number of results
            
        Returns:
            List of knowledge results
            
        Raises:
            KnowledgeError: If knowledge base not found or query fails
        """
        kb = self.get_knowledge_base(kb_name)
        if not kb:
            raise KnowledgeError(f"Knowledge base '{kb_name}' not found")
        
        if not kb.is_initialized():
            await kb.initialize()
        
        try:
            results = await kb.query(query, max_results)
            self.logger.debug(f"Queried knowledge base '{kb_name}' with {len(results)} results")
            return results
        except Exception as e:
            raise KnowledgeError(f"Failed to query knowledge base '{kb_name}': {e}")
    
    async def query_all_knowledge_bases(
        self, 
        query: str, 
        max_results_per_kb: int = 3
    ) -> Dict[str, List[KnowledgeResult]]:
        """
        Query all available knowledge bases.
        
        Args:
            query: Query string
            max_results_per_kb: Maximum results per knowledge base
            
        Returns:
            Dictionary mapping knowledge base names to results
        """
        all_results = {}
        
        for kb_name in self.knowledge_bases:
            try:
                results = await self.query_knowledge_base(kb_name, query, max_results_per_kb)
                if results:
                    all_results[kb_name] = results
            except Exception as e:
                self.logger.warning(f"Failed to query knowledge base '{kb_name}': {e}")
        
        return all_results
    
    def list_knowledge_bases(self) -> List[str]:
        """
        List all available knowledge base names.
        
        Returns:
            List of knowledge base names
        """
        return list(self.knowledge_bases.keys())
    
    def get_knowledge_base_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a knowledge base.
        
        Args:
            name: Knowledge base name
            
        Returns:
            Dictionary with knowledge base information or None if not found
        """
        kb = self.get_knowledge_base(name)
        if not kb:
            return None
        
        return {
            'name': kb.name,
            'initialized': kb.is_initialized(),
            'config': kb.config
        }
    
    async def cleanup(self) -> None:
        """Clean up all knowledge bases."""
        for kb in self.knowledge_bases.values():
            try:
                await kb.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up knowledge base '{kb.name}': {e}")
        
        self.knowledge_bases.clear()
        self.logger.info("Knowledge manager cleanup completed")