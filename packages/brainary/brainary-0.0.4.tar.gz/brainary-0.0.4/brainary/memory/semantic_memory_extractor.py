from typing import Any, Dict, List, Optional, Union
import json
import hashlib
from dataclasses import dataclass

# Try to import LLM, but don't fail if not available
try:
    from brainary.llm.llm import LLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLM = None

@dataclass
class SemanticSummary:
    """Represents a semantic summary of an object."""
    key_concepts: List[str]
    relationships: List[str]
    context: str
    importance_score: float
    semantic_hash: str
    summary_text: str

class SemanticMemoryExtractor:
    """Extracts semantic information from objects using LLM."""
    
    def __init__(self, llm_name: str = "gpt-4o-mini", cache_size: int = 1000):
        if not LLM_AVAILABLE:
            raise ImportError("LLM is not available. Please ensure brainary.llm is installed.")
        self.llm = LLM.get_by_name(llm_name)
        self.cache_size = cache_size
        self.semantic_cache = {}  # hash -> SemanticSummary
        
    def extract_semantic_info(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """
        Extract semantic information from an object.
        
        Args:
            obj: The object to extract semantic information from
            obj_name: Optional name/identifier for the object
            
        Returns:
            SemanticSummary containing extracted semantic information
        """
        # Generate hash for caching
        obj_str = str(obj)
        if obj_name:
            obj_str = f"{obj_name}: {obj_str}"
        
        obj_hash = hashlib.md5(obj_str.encode()).hexdigest()
        
        # Check cache first
        if obj_hash in self.semantic_cache:
            return self.semantic_cache[obj_hash]
        
        # Extract semantic information using LLM
        semantic_summary = self._extract_with_llm(obj, obj_name)
        semantic_summary.semantic_hash = obj_hash
        
        # Cache the result
        self._add_to_cache(obj_hash, semantic_summary)
        
        return semantic_summary
    
    def _extract_with_llm(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Extract semantic information using LLM."""
        
        # Check if LLM is available
        if not LLM_AVAILABLE or self.llm is None:
            return self._fallback_extraction(obj, obj_name)
        
        # Prepare the input for LLM analysis
        obj_repr = self._prepare_object_representation(obj, obj_name)
        
        # Create the extraction prompt
        prompt = self._create_extraction_prompt(obj_repr)
        
        try:
            # Get LLM response
            response = self.llm.request([prompt])
            if response and len(response) > 0:
                result_text = response[0]
            else:
                result_text = ""
            
            # Parse the LLM response
            semantic_summary = self._parse_llm_response(result_text, obj_repr)
            
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            semantic_summary = self._fallback_extraction(obj, obj_name)
        
        return semantic_summary
    
    def _prepare_object_representation(self, obj: Any, obj_name: str = None) -> str:
        """Prepare object representation for LLM analysis."""
        
        if hasattr(obj, 'render'):
            # Use object's render method if available
            obj_repr = obj.render()
        elif hasattr(obj, '__dict__'):
            # Use object's attributes
            obj_repr = str(obj.__dict__)
        else:
            # Use string representation
            obj_repr = str(obj)
        
        if obj_name:
            obj_repr = f"Object Name: {obj_name}\nObject Content: {obj_repr}"
        
        return obj_repr
    
    def _create_extraction_prompt(self, obj_repr: str) -> str:
        """Create the prompt for semantic extraction."""
        
        prompt = f"""
You are an expert semantic analyzer. Your task is to extract meaningful semantic information from objects and create insightful summaries.

## Object to Analyze
{obj_repr}

## Task
Analyze the object and extract semantic information in the following JSON format:

{{
    "key_concepts": ["concept1", "concept2", "concept3"],
    "relationships": ["relationship1", "relationship2"],
    "context": "Brief context description",
    "importance_score": 0.85,
    "summary_text": "A meaningful semantic summary"
}}

## Guidelines for Summary Text
The summary_text should be:
- **Meaningful**: Explain what the object represents semantically, not just its structure
- **Concise**: 1-2 sentences maximum
- **Insightful**: Capture the purpose, function, or meaning of the object
- **Contextual**: Relate to the domain or use case if apparent

## Examples of Good vs Bad Summaries:
- ❌ Bad: "Object Name: Review, Object Content: class Review with text and author fields"
- ✅ Good: "A user review system component that stores feedback with author attribution"
- ❌ Bad: "Class with name, age, and email properties"
- ✅ Good: "A person entity representing user profile data with contact information"

## Guidelines for Other Fields:
- **key_concepts**: Extract the most important semantic concepts, entities, or ideas (not field names)
- **relationships**: Describe how this object relates to other entities or concepts
- **context**: Provide domain context or situational information
- **importance_score**: Score from 0.0 to 1.0 based on semantic significance

## Output
Provide only the JSON response, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response: str, obj_repr: str) -> SemanticSummary:
        """Parse LLM response into SemanticSummary."""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return SemanticSummary(
                    key_concepts=data.get('key_concepts', []),
                    relationships=data.get('relationships', []),
                    context=data.get('context', ''),
                    importance_score=float(data.get('importance_score', 0.5)),
                    semantic_hash='',  # Will be set by caller
                    summary_text=data.get('summary_text', '')
                )
            else:
                # Fallback if JSON parsing fails
                return self._fallback_extraction_from_text(response, obj_repr)
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if parsing fails
            return self._fallback_extraction_from_text(response, obj_repr)
    
    def _fallback_extraction_from_text(self, response: str, obj_repr: str) -> SemanticSummary:
        """Fallback extraction when JSON parsing fails."""
        
        # Extract concepts from response text
        concepts = []
        if 'concept' in response.lower():
            # Try to extract concepts mentioned in response
            lines = response.split('\n')
            for line in lines:
                if 'concept' in line.lower() or 'key' in line.lower():
                    concepts.append(line.strip())
        
        # If no concepts found, use basic extraction
        if not concepts:
            return self._fallback_extraction(obj_repr, None)
        
        return SemanticSummary(
            key_concepts=concepts[:5],  # Limit to 5 concepts
            relationships=[],
            context="Extracted from LLM response",
            importance_score=0.5,
            semantic_hash='',
            summary_text=response[:200] if response else "No summary available"
        )
    
    def _fallback_extraction(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Fallback extraction when LLM is not available."""
        
        obj_str = str(obj)
        
        # Basic concept extraction
        concepts = []
        if hasattr(obj, '__class__'):
            concepts.append(obj.__class__.__name__)
        
        # Extract words that might be concepts
        words = obj_str.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                concepts.append(word)
        
        # Limit concepts
        concepts = concepts[:5]
        
        return SemanticSummary(
            key_concepts=concepts,
            relationships=[],
            context="Basic extraction",
            importance_score=0.3,
            semantic_hash='',
            summary_text=obj_str[:100] + "..." if len(obj_str) > 100 else obj_str
        )
    
    def _add_to_cache(self, obj_hash: str, summary: SemanticSummary):
        """Add semantic summary to cache with size management."""
        
        if len(self.semantic_cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.semantic_cache))
            del self.semantic_cache[oldest_key]
        
        self.semantic_cache[obj_hash] = summary
    
    def get_semantic_summary(self, obj: Any, obj_name: str = None) -> str:
        """Get a text summary of semantic information."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.summary_text
    
    def get_key_concepts(self, obj: Any, obj_name: str = None) -> List[str]:
        """Get key concepts from an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.key_concepts
    
    def get_importance_score(self, obj: Any, obj_name: str = None) -> float:
        """Get importance score for an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.importance_score
    
    def clear_cache(self):
        """Clear the semantic cache."""
        self.semantic_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.semantic_cache),
            'max_cache_size': self.cache_size,
            'cache_usage_percentage': (len(self.semantic_cache) / self.cache_size) * 100
        }

# Global extractor instance
_extractor_instance = None

def get_semantic_extractor(llm_name: str = "gpt-4o-mini") -> SemanticMemoryExtractor:
    """Get the global semantic extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        try:
            _extractor_instance = SemanticMemoryExtractor(llm_name)
        except ImportError:
            # Create a fallback extractor that only uses basic extraction
            _extractor_instance = FallbackSemanticExtractor()
    return _extractor_instance

class FallbackSemanticExtractor:
    """Fallback semantic extractor that doesn't require LLM."""
    
    def __init__(self):
        self.semantic_cache = {}
    
    def extract_semantic_info(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Extract semantic information using basic methods."""
        obj_str = str(obj)
        if obj_name:
            obj_str = f"{obj_name}: {obj_str}"
        
        obj_hash = hashlib.md5(obj_str.encode()).hexdigest()
        
        # Check cache first
        if obj_hash in self.semantic_cache:
            return self.semantic_cache[obj_hash]
        
        # Use basic extraction
        summary = self._fallback_extraction(obj, obj_name)
        summary.semantic_hash = obj_hash
        
        # Cache the result
        self.semantic_cache[obj_hash] = summary
        return summary
    
    def _fallback_extraction(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Basic semantic extraction without LLM."""
        obj_str = str(obj)
        
        # Basic concept extraction
        concepts = []
        if hasattr(obj, '__class__'):
            concepts.append(obj.__class__.__name__)
        
        # Extract words that might be concepts
        words = obj_str.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                concepts.append(word)
        
        # Limit concepts
        concepts = concepts[:5]
        
        return SemanticSummary(
            key_concepts=concepts,
            relationships=[],
            context="Basic extraction (LLM not available)",
            importance_score=0.3,
            semantic_hash='',
            summary_text=obj_str[:100] + "..." if len(obj_str) > 100 else obj_str
        )
    
    def get_semantic_summary(self, obj: Any, obj_name: str = None) -> str:
        """Get a text summary of semantic information."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.summary_text
    
    def get_key_concepts(self, obj: Any, obj_name: str = None) -> List[str]:
        """Get key concepts from an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.key_concepts
    
    def get_importance_score(self, obj: Any, obj_name: str = None) -> float:
        """Get importance score for an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.importance_score

def extract_semantic_info(obj: Any, obj_name: str = None) -> SemanticSummary:
    """Convenience function to extract semantic information."""
    extractor = get_semantic_extractor()
    return extractor.extract_semantic_info(obj, obj_name)

def get_semantic_summary(obj: Any, obj_name: str = None) -> str:
    """Convenience function to get semantic summary."""
    extractor = get_semantic_extractor()
    return extractor.get_semantic_summary(obj, obj_name)
