"""Immutable context model for document processing pipeline.

This module provides a strongly-typed, immutable alternative to the mutable
Dict[str, Any] analysis_context that was previously used throughout the pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from app.utils.processing_constants import ProcessingConstants


@dataclass(frozen=True)
class ProcessingContext:
    """Immutable context for document analysis pipeline phases.
    
    This dataclass replaces the mutable analysis_context dict to provide:
    - Type safety through explicit field typing
    - Immutability to prevent accidental state mutations
    - Clear documentation of context structure
    - Builder pattern support for incremental construction
    
    Attributes:
        extracted_text: Raw text extracted from document
        azure_result: Complete Azure Document Intelligence API response
        email: User email for document identification
        filename: Original document filename
        document_id: Unique identifier for this document processing session
        provider_metadata: Additional metadata from extraction provider
    """
    
    extracted_text: str
    azure_result: Dict[str, Any]
    email: str
    filename: str
    document_id: str
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_legacy_dict(cls, legacy_context: Dict[str, Any]) -> 'ProcessingContext':
        """Create ProcessingContext from legacy analysis_context dict.
        
        Args:
            legacy_context: The mutable dict used in the original implementation
            
        Returns:
            Immutable ProcessingContext with same data
            
        Raises:
            KeyError: If required keys are missing from legacy_context
            TypeError: If field types don't match expectations
        """
        try:
            return cls(
                extracted_text=legacy_context["extracted_text"],
                azure_result=legacy_context["azure_result"],
                email=legacy_context["email"],
                filename=legacy_context["filename"],
                document_id=legacy_context["document_id"],
                provider_metadata=legacy_context.get("provider_metadata", {})
            )
        except KeyError as e:
            raise ValueError(f"Required field missing from legacy context: {e}") from e
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convert ProcessingContext back to legacy analysis_context dict.
        
        This method supports gradual migration - services that haven't been
        updated to use ProcessingContext can still receive the familiar dict.
        
        Returns:
            Dict with same structure as original analysis_context
        """
        return {
            "extracted_text": self.extracted_text,
            "azure_result": self.azure_result,
            "email": self.email,
            "filename": self.filename,
            "document_id": self.document_id,
            "provider_metadata": self.provider_metadata
        }
    
    @property
    def has_azure_result(self) -> bool:
        """Check if Azure result contains meaningful data."""
        return bool(self.azure_result)
    
    @property
    def full_document_identifier(self) -> str:
        """Get the full document identifier used in various contexts."""
        return f"{self.email}_{self.filename}"


@dataclass
class ProcessingContextBuilder:
    """Builder pattern for incremental ProcessingContext construction.
    
    This builder allows pipeline phases to construct the context step by step
    while maintaining immutability of the final result.
    """
    
    extracted_text: Optional[str] = None
    azure_result: Optional[Dict[str, Any]] = None
    email: Optional[str] = None
    filename: Optional[str] = None
    document_id: Optional[str] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    
    def with_extracted_text(self, text: str) -> 'ProcessingContextBuilder':
        """Set extracted text and return builder for chaining."""
        self.extracted_text = text
        return self
    
    def with_azure_result(self, result: Dict[str, Any]) -> 'ProcessingContextBuilder':
        """Set Azure result and return builder for chaining."""
        self.azure_result = result
        return self
    
    def with_email(self, email: str) -> 'ProcessingContextBuilder':
        """Set email and return builder for chaining."""
        self.email = email
        return self
    
    def with_filename(self, filename: str) -> 'ProcessingContextBuilder':
        """Set filename and return builder for chaining."""
        self.filename = filename
        return self
    
    def with_document_id(self, document_id: str) -> 'ProcessingContextBuilder':
        """Set document ID and return builder for chaining."""
        self.document_id = document_id
        return self
    
    def with_provider_metadata(self, metadata: Dict[str, Any]) -> 'ProcessingContextBuilder':
        """Set provider metadata and return builder for chaining."""
        self.provider_metadata = metadata
        return self
    
    def build(self) -> ProcessingContext:
        """Build immutable ProcessingContext from current builder state.
        
        Returns:
            Immutable ProcessingContext instance
            
        Raises:
            ValueError: If required fields are not set
        """
        if not all([
            self.extracted_text is not None,
            self.azure_result is not None,
            self.email is not None,
            self.filename is not None,
            self.document_id is not None
        ]):
            missing_fields = [
                field for field, value in [
                    ("extracted_text", self.extracted_text),
                    ("azure_result", self.azure_result),
                    ("email", self.email),
                    ("filename", self.filename),
                    ("document_id", self.document_id)
                ]
                if value is None
            ]
            raise ValueError(f"Required fields not set: {missing_fields}")
        
        return ProcessingContext(
            extracted_text=self.extracted_text,
            azure_result=self.azure_result,
            email=self.email,
            filename=self.filename,
            document_id=self.document_id,
            provider_metadata=self.provider_metadata or {}
        )
    
    @classmethod
    def from_extraction_data(cls, 
                           extracted_data: Dict[str, Any],
                           email: str,
                           filename: str,
                           document_id: str) -> 'ProcessingContextBuilder':
        """Create builder from document extraction data.
        
        This is the primary factory method for creating contexts from
        the document extraction pipeline results.
        
        Args:
            extracted_data: Result from document extraction service
            email: User email for identification
            filename: Original document filename
            document_id: Unique processing session identifier
            
        Returns:
            Builder ready to build ProcessingContext
        """
        extracted_text = extracted_data.get("text", "")
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        provider_metadata = extracted_data.get("metadata", {})
        
        return cls().with_extracted_text(extracted_text) \
                  .with_azure_result(azure_result) \
                  .with_email(email) \
                  .with_filename(filename) \
                  .with_document_id(document_id) \
                  .with_provider_metadata(provider_metadata)