"""
Embedchain adapter for integrating Embedchain knowledge bases with Gnosari.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseKnowledgeBase, KnowledgeResult, KnowledgeProvider
from ..core.exceptions import KnowledgeError


class EmbedchainKnowledgeBase(BaseKnowledgeBase):
    """
    Embedchain implementation of the knowledge base interface.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Embedchain knowledge base.
        
        Args:
            name: Knowledge base name
            config: Optional Embedchain configuration
        """
        super().__init__(name, config)
        self.embedchain_app = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the Embedchain application."""
        if self._initialized:
            return
        
        try:
            from embedchain import App
            
            # Create Embedchain app with configuration
            embedchain_config = self.config.get('embedchain', {})
            self.embedchain_app = App.from_config(config=embedchain_config)
            
            self._initialized = True
            self.logger.info(f"Initialized Embedchain knowledge base '{self.name}'")
            
        except ImportError:
            raise KnowledgeError("Embedchain not installed. Install with: pip install embedchain")
        except Exception as e:
            raise KnowledgeError(f"Failed to initialize Embedchain knowledge base '{self.name}': {e}")
    
    async def add_data(self, data: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add data to the Embedchain knowledge base.
        
        Args:
            data: Data content or URL to add
            source: Source identifier
            metadata: Optional metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Determine data type based on content
            if data.startswith(('http://', 'https://')):
                # It's a URL
                self.embedchain_app.add(data, data_type='web_page')
            elif data.endswith('.pdf'):
                # It's a PDF file
                self.embedchain_app.add(data, data_type='pdf_file')
            elif data.endswith(('.txt', '.md')):
                # It's a text file
                self.embedchain_app.add(data, data_type='text_file')
            else:
                # Treat as raw text
                self.embedchain_app.add(data, data_type='text')
            
            self.logger.debug(f"Added data to Embedchain knowledge base '{self.name}': {source}")
            
        except Exception as e:
            raise KnowledgeError(f"Failed to add data to knowledge base '{self.name}': {e}")
    
    async def query(self, query: str, max_results: int = 5) -> List[KnowledgeResult]:
        """
        Query the Embedchain knowledge base.
        
        Args:
            query: Query string
            max_results: Maximum number of results
            
        Returns:
            List of knowledge results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Query Embedchain
            response = self.embedchain_app.query(query)
            
            # Convert response to KnowledgeResult format
            # Note: Embedchain typically returns a string response
            # For more detailed results, we'd need to access the underlying retrieval
            results = [
                KnowledgeResult(
                    content=response,
                    source=self.name,
                    score=1.0,  # Embedchain doesn't provide scores by default
                    metadata={'query': query}
                )
            ]
            
            return results[:max_results]
            
        except Exception as e:
            raise KnowledgeError(f"Failed to query knowledge base '{self.name}': {e}")
    
    async def delete_data(self, source: str) -> bool:
        """
        Delete data from the Embedchain knowledge base.
        
        Args:
            source: Source identifier
            
        Returns:
            True if data was deleted
        """
        # Embedchain doesn't have a direct delete method in the basic interface
        # This would need to be implemented based on the specific Embedchain version
        self.logger.warning(f"Delete operation not implemented for Embedchain knowledge base '{self.name}'")
        return False
    
    async def cleanup(self) -> None:
        """Clean up Embedchain resources."""
        if self.embedchain_app:
            # Embedchain cleanup if available
            self.embedchain_app = None
        self._initialized = False


class EmbedchainProvider(KnowledgeProvider):
    """
    Provider for creating Embedchain knowledge bases.
    """
    
    def create_knowledge_base(
        self, 
        name: str, 
        kb_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseKnowledgeBase:
        """
        Create an Embedchain knowledge base.
        
        Args:
            name: Knowledge base name
            kb_type: Type (should be supported by Embedchain)
            config: Optional configuration
            
        Returns:
            EmbedchainKnowledgeBase instance
        """
        return EmbedchainKnowledgeBase(name, config)
    
    def get_supported_types(self) -> List[str]:
        """
        Get supported knowledge base types.
        
        Returns:
            List of supported types
        """
        return [
            'website',
            'documents', 
            'text',
            'pdf',
            'web_page',
            'youtube_video',
            'github_repo'
        ]