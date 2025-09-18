#filterhero/schemas.py

import re
from typing import List, Union, Dict, Any, Optional, Tuple, Literal
from dataclasses import dataclass
from typing import Any, Optional
import time


from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import uuid, datetime as _dt, time
import tiktoken
from llmservice import GenerationResult
from pydantic import BaseModel, Field
# 

@dataclass
class CorpusPayload:
    corpus:       str                # Text input or original JSON string
    corpus_type:  str                # "html", "json" or "text"
    reduced_html: Optional[str]      # Only when HTML is reduced
    error:        Optional[str] = None    # ← give a default

@dataclass
class CorpusPayload:
    corpus:        Any                     # str or dict
    corpus_type:   str                     # "html" | "json" | "text"
    reduced_html:  Optional[str] = None
    # reduce_op:     Optional[Any] = None   # holds the full ReduceOperation object
    error:         Optional[str] = None

from dataclasses import dataclass, field
from typing import List, Optional




@dataclass
class WhatToRetain:
    """
    Specification for FilterHero's "guidable selective semantic context chunking".

    Parameters
    ----------
    name : str
         A short identifier (e.g., "product name", "person profile").
    desc : Optional[str]
       An LLM-readable, definitive description of the item to filter.  
        For example, for a product name you might write:  
        "Title of the product as it is listed."
    include_context_chunk : bool
        If True (default), instructs the LLM to retain the entire semantic
        content relevant to this item.
    custom_context_chunk_desc : Optional[str]
        Extra guidance that refines what "context chunk" means.  
        Example: "Only non-technical sales information—exclude technical
        attributes."
    wrt_to_source_filter_desc : Optional[str]
        Free-text relevance hint that narrows the selection with respect to the
        page's main subject.  
        Examples: "Primary product only";  
        "Should not include side products like recommendations."
    
    context_contradiction_check : bool
        If True, instructs the LLM to discard chunks that clearly contradict
        `target_context`, while retaining any ambiguous or matching ones.
    text_rules : Optional[List[str]]
        Additional bullet-point rules to refine inclusion/exclusion logic.
    """
    
    # ───────── core fields ─────────
    name: str
    desc: Optional[str] = None
    include_context_chunk: bool = True
    custom_context_chunk_desc: Optional[str] = None
    wrt_to_source_filter_desc: Optional[str] = None
    
    # ───────── context targeting ────
    identifier_context_contradiction_check: bool = False
    
    # ───────── extra rules ──────────
    text_rules: Optional[List[str]] = None

    regex_validator: Optional[str] = None      # format guard

    # example
    example: Optional[str] = None

    # ─────── prompt builder ────────
    def compile(self) -> str:
        parts: List[str] = [f"INTERESTED Target INFORMATION: {self.name}"]
        
        if self.desc:
            parts.append(f"     Target Info Description: {self.desc}")

        if self.example:
            parts.append(f"Example: {self.example}")


        if self.include_context_chunk:
            ctx = (
                self.custom_context_chunk_desc
                or "Include the entire semantic block that represents this item."
            )
            parts.append(f"Context guidance: {ctx}")

        if self.wrt_to_source_filter_desc:
            parts.append(
                f"Relevance hint w.r.t. page source: {self.wrt_to_source_filter_desc}"
            )

        

        if self.identifier_context_contradiction_check:
            parts.append(
                "Contradiction rule: Discard chunks that clearly contradict the "
                "target context above, but retain any that might still be relevant."
            )

        if self.text_rules:
            parts.append("    Additional rules: " + "; ".join(self.text_rules))

        return "\n".join(parts)
    


    # ─────── prompt builder ────────
    def compile_parser(self) -> str:
        parts: List[str] = [f"keyword: {self.name}"]

        if self.desc:
            parts.append(f"keyword description: {self.desc}")

        # if self.include_context_chunk:
        #     ctx = (
        #         self.custom_context_chunk_desc
        #         or "Include the entire semantic block that represents this item."
        #     )
        #     parts.append(f"Context guidance: {ctx}")

     
        if self.text_rules:
            parts.append("Additional rules: " + "; ".join(self.text_rules))

        return "\n".join(parts)
    




#semantics_exist_validation
#must_exist_keywords
#regex_validation






@dataclass
class FilterOp:
    success: bool                   # Whether filtering succeeded
    content: Any                    # The filtered corpus (text) for parsing
    usage: Optional[Dict[str, Any]] # LLM usage stats (tokens, cost, etc.)
    elapsed_time: float             # Time in seconds that the filter step took
   
    
    generation_result: Optional[Any] = None  # holds the GenerationResult from LLM call
    error: Optional[str] = None  
    start_time: Any = None
    filtered_data_token_size: Optional[Any] = None  # Add this parameter
    filter_strategy: Optional[Any] = None
    
    SSM: Optional[Any] = None # semantic section mapping

   
    
    # New fields for subtractive mode
    filter_mode: Optional[str] = None  # "extractive" or "subtractive"
    deletions_applied: Optional[List[Dict]] = None  # Line ranges deleted
    original_line_count: Optional[int] = None
    retained_line_count: Optional[int] = None
    lines_removed: Optional[int] = None

    @classmethod
    def from_result(
        cls,
       
        content: Any,
        usage: Optional[Dict[str, Any]],
        start_time: float = None,
        generation_result: Optional[Any] = None,  
        success: bool = True,
        error: Optional[str] = None, 
        SSM: Optional[str] = None, 
        filtered_data_token_size = None, 
        filter_strategy: Optional[Any] = None,
        filter_mode: Optional[str] = None,
        deletions_applied: Optional[List[Dict]] = None,
        original_line_count: Optional[int] = None,
        retained_line_count: Optional[int] = None,
        lines_removed: Optional[int] = None
    ) -> "FilterOp":
        elapsed = time.time() - start_time
        return cls(
            success=success,
            content=content,
            usage=usage,
            elapsed_time=elapsed,
          
            generation_result=generation_result,  # ← Set it here
            error=error, 
            SSM=SSM, 
            start_time=start_time,
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=filter_strategy,
            filter_mode=filter_mode,
            deletions_applied=deletions_applied,
            original_line_count=original_line_count,
            retained_line_count=retained_line_count,
            lines_removed=lines_removed
        )
    

    @staticmethod
    def _save_string_as_txt(
        value: str,
        *,
        stem: str,
        filename: Optional[str],
        dir: str | Path,
        overwrite: bool,
        raise_if_empty: bool,
        encoding: str,
    ) -> Path:
        if not isinstance(value, str):
            raise TypeError("Payload must be str to be saved as .txt")

        if value == "" and raise_if_empty:
            raise RuntimeError("Payload is empty – nothing to save")

        if filename is None:
            filename = f"{stem}-{uuid.uuid4().hex}.txt"
        elif not filename.lower().endswith(".txt"):
            filename += ".txt"

        path = Path(dir) / filename
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists (overwrite=False)")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding=encoding)
        return path
    
    
    def save_content_to_txt(
        self,
        filename: str | None = None,
        *,
        dir: str | Path = ".",
        overwrite: bool = False,
        raise_if_empty: bool = True,
        encoding: str = "utf-8",
    ) -> Path:
        """Persist ``self.content`` as *.txt* and return the path."""
        path = self._save_string_as_txt(
            self.content,
            stem="content",
            filename=filename,
            dir_=dir,
            overwrite=overwrite,
            raise_if_empty=raise_if_empty,
            encoding=encoding,
        )
      
        return path
    

    def save_content(
        self,
        format: str = "json",
        filename: Optional[str] = None,
        dir: str = "."
    ) -> Path:
        """
        Save the extraction results (LLM output) to a file.
        
        Args:
            format: Output format ('json' or 'markdown')
            filename: Custom filename (without extension)
            dir: Directory to save in
            
        Returns:
            Path to the saved file
        """
        if not self.content:
            raise ValueError("No extraction content to save")
        
        # Determine file extension
        ext = '.json' if format == 'json' else '.md'

        import json
        from datetime import datetime, timezone
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_content_{timestamp}{ext}"
        elif not filename.endswith(ext):
            filename += ext
        
        # Create path
        path = Path(dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save based on format
        if format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.content, f, indent=2, ensure_ascii=False, default=str)
        else:  # markdown format
            # If content is already a string (markdown from LLM), save directly
            if isinstance(self.content, str):
                path.write_text(self.content, encoding='utf-8')
            # If content is JSON structure, convert to readable text
            elif isinstance(self.content, (dict, list)):
                content_str = json.dumps(self.content, indent=2, ensure_ascii=False, default=str)
                path.write_text(content_str, encoding='utf-8')
            else:
                path.write_text(str(self.content), encoding='utf-8')
        
        return path

  
@dataclass
class FilterChainOp:
    """Result of a filter chain operation containing multiple sequential filter stages."""
    
    success: bool
    content: Optional[str]  # Result of last filtration
    elapsed_time: float
    generation_results: List[GenerationResult]  # Results from each stage
    usage: Optional[Dict[str, Any]]  # Combined usage from all stages
    error: Optional[str]
    start_time: float
    filtered_data_token_size: Optional[int]  # Token size of final content
    stages_config: List[Tuple[List[WhatToRetain], str]]  # Original stages parameter
    reduction_details: List[Dict[str, int]]  # Token reduction at each stage
    filterops: List[FilterOp]  # Individual FilterOp results from each stage

    


@dataclass
class ProcessResult:
    fast_op:   Optional[FilterOp]   # ready-to-return FilterOp (JSON path)
    corpus:    Optional[str]        # always a string if we need the LLM
    reduced:   Optional[str]        # reduced HTML snippet (may be None)
    

