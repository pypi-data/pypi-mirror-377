# extracthero/filterhero.py
# run with:  python -m extracthero.filterhero
"""
FilterHero — the "filter" phase of ExtractHero.
• Normalises raw input (HTML / JSON / dict / plain-text).
• Optionally reduces HTML to visible text.
• Uses a JSON fast-path when possible; otherwise builds LLM prompts.
"""

from __future__ import annotations
import tiktoken
import json as _json
from dataclasses import dataclass
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

from llmservice import GenerationResult
from extracthero.myllmservice import MyLLMService, TocOutput
from extracthero.schemas import (
    ExtractConfig,
    FilterOp,
    CorpusPayload,   
    WhatToRetain, 
    ProcessResult,
    FilterChainOp

)

from extracthero.utils import load_html
from extracthero.sample_dicts import sample_page_dict
import asyncio

from extracthero.filter_engine import FilterEngine



import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=".*extracthero.filterhero.*"
)


encoding = tiktoken.encoding_for_model("gpt-4o-mini")




# ─────────────────────────────────────────────────────────────────────────────
class FilterHero:
    def __init__(
        self,
        config: Optional[ExtractConfig] = None,
        llm: Optional[MyLLMService] = None,
    ):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()

        self.engine= FilterEngine(llm_service=self.llm)

    # ──────────────────────── public orchestrator ────────────────────────
    def run(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_strategy: str = "relaxed",
        filter_mode: str = "extractive",  # New parameter: "extractive" or "subtractive"
        max_line_length_for_indexing: Optional[int] = 200,  # New parameter for line truncation in indexed content
        line_format: str = "[{n}]",  # New parameter for line number format
        model_name: Optional[str] = None  # Model to use (e.g., "gpt-4.1-mini", "gpt-5")
    ) -> FilterOp:
        """
        End-to-end filter phase with support for both extractive and subtractive modes.
        
        Parameters
        ----------
        filter_mode : str
            "extractive" - Traditional mode, LLM outputs filtered content (default)
            "subtractive" - New mode, LLM outputs line numbers to delete and we delete them via code
        max_line_length_for_indexing : int or None
            For subtractive mode: max characters per line before truncation in the indexed/numbered content shown to LLM.
            Only affects what the LLM sees, not the final output.
            Default 200 to prevent very long lines from consuming tokens.
            Set to None for no truncation.
        line_format : str
            Format for line numbers in subtractive mode. Use {n} for number.
            Examples: "[{n}]" → "[1]", "L{n}:" → "L1:", "{n:04d}|" → "0001|"
            Default: "[{n}]"
        """
       
        
        if filter_mode == "subtractive":
            return self._run_subtractive(text, extraction_spec, filter_strategy, max_line_length_for_indexing, line_format, model_name)
        else:
            return self._run_extractive(text, extraction_spec, filter_strategy, model_name)
    
    def _run_extractive(self, text, extraction_spec, filter_strategy, model_name=None):

        ts = time()
        """Existing extractive filtering logic"""
        content = None
        filtered_data_token_size = None
        
        # Calculate original line count
        if isinstance(text, str):
            original_lines = text.split('\n')
        elif isinstance(text, dict):
            original_lines = _json.dumps(text, indent=2).split('\n')
        else:
            original_lines = str(text).split('\n')
        
        original_line_count = len(original_lines)

        gen_result = self.engine.execute_filtering(
            text, 
            extraction_spec, 
            filter_strategy,
            model_name
        )

        # Calculate retained line count and other metrics
        retained_line_count = None
        
        if gen_result.success:
            content = gen_result.content
            if content is not None:
                try:
                    filtered_data_token_size = len(encoding.encode(content))
                    # Calculate retained line count
                    filtered_lines = content.split('\n')
                    retained_line_count = len(filtered_lines)
                except Exception:
                    filtered_data_token_size = None

        return FilterOp.from_result(
            config=self.config,
            content=content,
            usage=gen_result.usage,
            generation_result=gen_result,
            start_time=ts,
            success=gen_result.success,
            error=None if gen_result.success else "LLM filter failed",
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=filter_strategy,
            filter_mode="extractive",
            original_line_count=original_line_count,
            retained_line_count=retained_line_count
        )
    
    def _run_subtractive(self,
                        text,
                        extraction_spec,
                        filter_strategy,
                        max_line_length_for_indexing=200,
                        line_format="[{n}]",
                        approach="semantic-section-mapping",
                        model_name=None):
        
        """
        New subtractive filtering logic using line-based deletion.
        
        Parameters
        ----------
        max_line_length_for_indexing : int or None
            Max characters per line in indexed/numbered content shown to LLM.
            Only affects LLM input, not final output.
            Default 200 to prevent very long lines from consuming tokens.
            Set to None for no truncation.
        line_format : str
            Format for line numbers. Default "[{n}]" gives [1], [2], etc.
        """
        start_time = time()
        
        # Convert dict to string if needed
        if isinstance(text, dict):
            text = _json.dumps(text, indent=2)
        
        # Split into lines for processing
        original_lines = text.split('\n')
        
        # Step 1: Create numbered content for LLM
        numbered_content = self._prepare_numbered_content(
            original_lines, 
            max_line_length=max_line_length_for_indexing,
            line_format=line_format
        )
        
        # Step 2: Get ToC sections from LLM
        gen_result = self.engine.execute_subtractive_filtering(
            numbered_content,
            extraction_spec,
            filter_strategy,
            model_name
        )
        
        # Step 3: Parse ToC result and apply filtering
        if gen_result.success and gen_result.content:
            # The content should be a TocOutput object from get_content_toc()
            if not isinstance(gen_result.content, TocOutput):
                return FilterOp.from_result(
                    config=self.config,
                    content=None,
                    usage=gen_result.usage,
                    generation_result=gen_result,
                    start_time=start_time,
                    success=False,
                    error=f"Expected TocOutput but got {type(gen_result.content).__name__}",
                    filtered_data_token_size=None,
                    filter_strategy=filter_strategy,
                    filter_mode="subtractive"
                )
            
            SSM_output = gen_result.content
            
            # Convert SSM sections to lines to keep
            lines_to_keep = self._convert_toc_to_lines_to_keep(SSM_output, len(original_lines))
            
            # Build filtered text from kept lines
            filtered_text = self._build_filtered_text(original_lines, lines_to_keep)
            
            # Calculate metrics
            lines_removed = len(original_lines) - len(lines_to_keep)
            filtered_data_token_size = None
            if filtered_text:
                try:
                    filtered_data_token_size = len(encoding.encode(filtered_text))
                except Exception:
                    filtered_data_token_size = None
            
            # Build deletion ranges for metadata
            deletions_applied = self._build_deletion_ranges(lines_to_keep, len(original_lines), SSM_output)
            
            return FilterOp.from_result(
                config=self.config,
                content=filtered_text,
                usage=gen_result.usage,
                generation_result=gen_result,
                start_time=start_time,
                success=True,
                error=None,
                SSM=SSM_output, 
                filtered_data_token_size=filtered_data_token_size,
                filter_strategy=filter_strategy,
                filter_mode="subtractive",
                deletions_applied=deletions_applied,
                original_line_count=len(original_lines),
                retained_line_count=len(lines_to_keep),
                lines_removed=lines_removed
            )
        else:
            return FilterOp.from_result(
                config=self.config,
                content=None,
                usage=gen_result.usage if gen_result else None,
                generation_result=gen_result,
                start_time=start_time,
                success=False,
                error=f"Subtractive filtering failed: {gen_result.error_message if gen_result and hasattr(gen_result, 'error_message') else 'Unknown error'}",
                filtered_data_token_size=None,
                filter_strategy=filter_strategy,
                filter_mode="subtractive"
            )
    
    def _prepare_numbered_content(self, lines, max_line_length=None, line_format="[{n}]"):
        """
        Convert lines to numbered content for LLM processing.
        
        Parameters
        ----------
        lines : list
            List of text lines to number
        max_line_length : int or None
            Maximum characters per line before truncation. 
            If None, no truncation is applied.
            Default None means show full lines.
        line_format : str
            Format string for line numbers. Use {n} for the line number.
            Examples: "[{n}]" → "[1]", "L{n}:" → "L1:", "{n:04d}|" → "0001|"
            Default: "[{n}]"
        
        Returns
        -------
        str
            Numbered content with optional truncation for LLM processing
        """
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            # Optionally truncate long lines
            if max_line_length and len(line) > max_line_length:
                display_line = f"{line[:max_line_length]}..."
            else:
                display_line = line
            
            # Format the line number
            line_prefix = line_format.format(n=i)
            numbered_lines.append(f"{line_prefix} {display_line}")
        
        return '\n'.join(numbered_lines)
    
    def _parse_deletion_response(self, llm_response):
        """Parse LLM's deletion response into structured format"""
        try:
            if isinstance(llm_response, str):
                data = _json.loads(llm_response)
            else:
                data = llm_response
            
            return data.get('deletions', [])
        except Exception as e:
            print(f"Failed to parse deletion response: {e}")
            return []
    
    def _should_keep_section(self, section) -> bool:
        """
        Determine if a section should be kept based on its properties.
        
        This method centralizes the decision logic for section filtering,
        making it easy to modify the criteria or add new strategies.
        
        Parameters
        ----------
        section : TocSection
            A section from the Table of Contents
            
        Returns
        -------
        bool
            True if the section should be kept, False if it should be deleted
        """
        # Always keep if marked as content
        if section.is_content:
            return True
        
        # Always keep code and content categories, even if not marked as is_content
        # (This handles cases where LLM might mark code blocks as non-content by mistake)
        if section.category in ["code", "content"]:
            return True
        
        # For navigation, footer, and header categories:
        # Only delete them if is_content is explicitly False
        if section.category in ["navigation", "footer", "header"]:
            if section.is_content is False:
                return False  # Delete only if explicitly marked as non-content
            return True  # Keep if is_content is True or unclear
        
        # For other categories (metadata, etc.), keep by default unless explicitly non-content
        return section.is_content if section.is_content is not None else True
    
    def _convert_toc_to_lines_to_keep(self, toc_output: TocOutput, total_lines: int) -> set:
        """
        Convert ToC sections marked as content into a set of line numbers to keep.
        
        Parameters
        ----------
        toc_output : TocOutput
            The Table of Contents with sections marked as content/non-content
        total_lines : int
            Total number of lines in the original document
            
        Returns
        -------
        set
            Set of line numbers (1-indexed) to keep in the filtered output
        """
        lines_to_keep = set()
        for section in toc_output.sections:
            if self._should_keep_section(section):
                # Keep lines from this section
                for line_num in range(section.start_line, section.end_line + 1):
                    if 1 <= line_num <= total_lines:
                        lines_to_keep.add(line_num)
        return lines_to_keep
    
    
    
    def _build_filtered_text(self, original_lines: List[str], lines_to_keep: set) -> str:
        """
        Build filtered text by keeping only specified line numbers.
        
        Parameters
        ----------
        original_lines : List[str]
            Original document lines
        lines_to_keep : set
            Set of line numbers (1-indexed) to keep
            
        Returns
        -------
        str
            Filtered text containing only the kept lines
        """
        filtered_lines = []
        for i, line in enumerate(original_lines, 1):
            if i in lines_to_keep:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _build_deletion_ranges(self, lines_to_keep: set, total_lines: int, ssm_output: Optional[TocOutput] = None) -> List[Dict]:
        """
        Build deletion ranges from lines to keep for metadata tracking.
        
        Parameters
        ----------
        lines_to_keep : set
            Set of line numbers (1-indexed) to keep
        total_lines : int
            Total number of lines in the original document
        ssm_output : Optional[TocOutput]
            The SSM output containing section information
            
        Returns
        -------
        List[Dict]
            List of deletion ranges with start_line, end_line, and section name
        """
        deletions_applied = []
        
        # If we have SSM data, use it to get section names for deleted ranges
        if ssm_output:
            for section in ssm_output.sections:
                # Check if this section should be deleted (not in lines_to_keep)
                if not self._should_keep_section(section):
                    deletions_applied.append({
                        "start_line": section.start_line,
                        "end_line": section.end_line,
                        "name": section.name,
                        "category": section.category,
                        "is_content": section.is_content,
                        "is_navigation": section.is_navigation
                    })
        else:
            # Fallback to the old method if no SSM data
            current_deletion_start = None
            
            for i in range(1, total_lines + 1):
                if i not in lines_to_keep:
                    if current_deletion_start is None:
                        current_deletion_start = i
                else:
                    if current_deletion_start is not None:
                        deletions_applied.append({
                            "start_line": current_deletion_start,
                            "end_line": i - 1,
                            "name": "Unknown section"
                        })
                        current_deletion_start = None
            
            # Handle deletion at the end
            if current_deletion_start is not None:
                deletions_applied.append({
                    "start_line": current_deletion_start,
                    "end_line": total_lines,
                    "name": "Unknown section"
                })
        
        return deletions_applied
    
    def _validate_line_ranges(self, deletions, total_lines):
        """Validate that line ranges are within bounds"""
        valid_deletions = []
        
        for deletion in deletions:
            start = deletion.get('start_line', 0)
            end = deletion.get('end_line', 0)
            
            if 1 <= start <= total_lines and 1 <= end <= total_lines and start <= end:
                valid_deletions.append(deletion)
            else:
                print(f"Invalid deletion range: {start}-{end} (total lines: {total_lines})")
        
        return valid_deletions
    
    def _apply_line_deletions(self, lines, deletions):
        """Apply deletions to get filtered text"""
        lines_to_delete = set()
        
        for deletion in deletions:
            for line_num in range(deletion['start_line'], deletion['end_line'] + 1):
                lines_to_delete.add(line_num)
        
        filtered_lines = []
        for i, line in enumerate(lines, 1):
            if i not in lines_to_delete:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    
    async def run_async(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_strategy: str = "contextual",
        filter_mode: str = "extractive",  # New parameter
        max_line_length_for_indexing: Optional[int] = 200,
        line_format: str = "[{n}]",
        model_name: Optional[str] = None
    ) -> FilterOp:
        """Async end-to-end filter phase with support for both modes."""
        ts = time()
        
        if filter_mode == "subtractive":
            # Subtractive mode doesn't have async implementation yet in engine
            # For now, we'll use sync version in async wrapper
            # TODO: Implement async subtractive filtering in engine
            return self._run_subtractive(text, extraction_spec, filter_strategy, max_line_length_for_indexing, line_format)
        else:
            # Extractive mode (existing async implementation)
            content = None
            filtered_data_token_size = None
            
            gen_result = await self.engine.execute_filtering_async(
                text, 
                extraction_spec, 
                filter_strategy,
                model_name  
            )

            if gen_result.success:
                content = gen_result.content
                if content is not None:
                    try:
                        filtered_data_token_size = len(encoding.encode(content))
                    except Exception:
                        filtered_data_token_size = None

            return FilterOp.from_result(
                config=self.config,
                content=content,
                usage=gen_result.usage,
                generation_result=gen_result,
                start_time=ts,
                success=gen_result.success,
                error=None if gen_result.success else "LLM filter failed",
                filtered_data_token_size=filtered_data_token_size,
                filter_strategy=filter_strategy,
                filter_mode="extractive"
            )
    

    def _combine_usage(self, usage_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Combine usage dictionaries from multiple stages."""
        if not usage_list:
            return None
        
        combined = {}
        
        # Sum numeric values
        for usage in usage_list:
            for key, value in usage.items():
                if isinstance(value, (int, float)):
                    combined[key] = combined.get(key, 0) + value
                elif key not in combined:
                    # For non-numeric values, keep the first occurrence
                    combined[key] = value
        
        return combined if combined else None
    

    def _calculate_reduction_details(
        self, 
        filter_ops: List[FilterOp], 
        initial_content: str
    ) -> List[Dict[str, int]]:
        """Calculate token reduction details for each stage."""
        reduction_details = []
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        
        try:
            # Calculate initial token size
            current_content = initial_content
            current_token_size = len(encoding.encode(current_content))
            
            for op in filter_ops:
                if op.success and op.content:
                    new_token_size = len(encoding.encode(op.content))
                    reduction_details.append({
                        "source_token_size": current_token_size,
                        "filtered_token_size": new_token_size
                    })
                    current_content = op.content
                    current_token_size = new_token_size
                else:
                    # Failed operation - no reduction
                    reduction_details.append({
                        "source_token_size": current_token_size,
                        "filtered_token_size": current_token_size
                    })
        
        except Exception:
            # If token calculation fails, return empty list
            reduction_details = []
        
        return reduction_details
    

    def chain(
        self,
        text: str | Dict[str, Any],
        stages: List[Tuple[List[WhatToRetain], str]],
    ) -> FilterChainOp:
        """
        Chain multiple filter operations synchronously.
        
        Parameters
        ----------
        text : str | Dict[str, Any]
            Initial input
        stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples
            
        Returns
        -------
        FilterChainOp
            Complete result of the filter chain
        """
        start_time = time()
        filter_ops = []
        current_input = text
        
        # Convert initial input to string if needed
        if isinstance(text, dict):
            initial_content = str(text)  # You might want to JSON serialize this
        else:
            initial_content = text
        
        # Execute each stage
        for extraction_spec, filter_strategy in stages:
            filter_op = self.run(current_input, extraction_spec, filter_strategy)
            filter_ops.append(filter_op)
            
            if not filter_op.success:
                break  # Stop on first failure
                
            current_input = filter_op.content
        
        # Build the result
        if not filter_ops:
            return FilterChainOp(
                success=False,
                content=None,
                elapsed_time=time() - start_time,
                generation_results=[],
                usage=None,
                error="No filter operations completed",
                start_time=start_time,
                filtered_data_token_size=None,
                stages_config=stages,
                reduction_details=[],
                filterops=[]
            )
        
        # Determine overall success (all stages must succeed)
        overall_success = all(op.success for op in filter_ops)
        
        # Get final content (from last successful operation)
        final_content = None
        for op in reversed(filter_ops):
            if op.success and op.content:
                final_content = op.content
                break
        
        # Calculate final token size
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        final_token_size = None
        if final_content:
            try:
                final_token_size = len(encoding.encode(final_content))
            except Exception:
                final_token_size = None
        
        # Combine usage from all stages
        combined_usage = self._combine_usage([op.usage for op in filter_ops if op.usage])
        
        # Extract generation results
        generation_results = [op.generation_result for op in filter_ops if op.generation_result]
        
        # Calculate reduction details
        reduction_details = self._calculate_reduction_details(filter_ops, initial_content)
        
        # Determine error message
        error_message = None
        if not overall_success:
            failed_ops = [op for op in filter_ops if not op.success]
            if failed_ops:
                error_message = f"Stage {filter_ops.index(failed_ops[0]) + 1} failed: {failed_ops[0].error}"
        
        return FilterChainOp(
            success=overall_success,
            content=final_content,
            elapsed_time=time() - start_time,
            generation_results=generation_results,
            usage=combined_usage,
            error=error_message,
            start_time=start_time,
            filtered_data_token_size=final_token_size,
            stages_config=stages,
            reduction_details=reduction_details,
            filterops=filter_ops
        )
    

    

    

    async def chain_async(
        self,
        text: str | Dict[str, Any],
        stages: List[Tuple[List[WhatToRetain], str]],
    ) -> FilterChainOp:
        """
        Chain multiple filter operations asynchronously.
        
        Parameters
        ----------
        text : str | Dict[str, Any]
            Initial input
        stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples
            
        Returns
        -------
        FilterChainOp
            Complete result of the filter chain
        """
        start_time = time()
        filter_ops = []
        current_input = text
        
        # Convert initial input to string if needed
        if isinstance(text, dict):
            initial_content = str(text)  # You might want to JSON serialize this
        else:
            initial_content = text
        
        # Execute each stage
        for extraction_spec, filter_strategy in stages:
            filter_op = await self.run_async(current_input, extraction_spec, filter_strategy)
            filter_ops.append(filter_op)
            
            if not filter_op.success:
                break  # Stop on first failure
                
            current_input = filter_op.content
        
        # Build the result (same logic as sync version)
        if not filter_ops:
            return FilterChainOp(
                success=False,
                content=None,
                elapsed_time=time() - start_time,
                generation_results=[],
                usage=None,
                error="No filter operations completed",
                start_time=start_time,
                filtered_data_token_size=None,
                stages_config=stages,
                reduction_details=[],
                filterops=[]
            )
        
        # Determine overall success
        overall_success = all(op.success for op in filter_ops)
        
        # Get final content
        final_content = None
        for op in reversed(filter_ops):
            if op.success and op.content:
                final_content = op.content
                break
        
        # Calculate final token size
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        final_token_size = None
        if final_content:
            try:
                final_token_size = len(encoding.encode(final_content))
            except Exception:
                final_token_size = None
        
        # Combine usage and build results
        combined_usage = self._combine_usage([op.usage for op in filter_ops if op.usage])
        generation_results = [op.generation_result for op in filter_ops if op.generation_result]
        reduction_details = self._calculate_reduction_details(filter_ops, initial_content)
        
        # Error handling
        error_message = None
        if not overall_success:
            failed_ops = [op for op in filter_ops if not op.success]
            if failed_ops:
                error_message = f"Stage {filter_ops.index(failed_ops[0]) + 1} failed: {failed_ops[0].error}"
        
        return FilterChainOp(
            success=overall_success,
            content=final_content,
            elapsed_time=time() - start_time,
            generation_results=generation_results,
            usage=combined_usage,
            error=error_message,
            start_time=start_time,
            filtered_data_token_size=final_token_size,
            stages_config=stages,
            reduction_details=reduction_details,
            filterops=filter_ops
        )
    




def example_chain_usage():
    filter_hero = FilterHero()

    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    
    
    stages = [
        ([WhatToRetain(name="voltage", desc="all voltage information")], "contextual"),
        # ([WhatToRetain(name="voltage", desc="only voltage related information")], "inclusive"),
        # ([WhatToRetain(name="voltage", desc="only voltage related information")], "contextual"),
        ([WhatToRetain(name="voltage", desc="only voltage related information")], "base"),
    
    ]
    
    chain_result = filter_hero.chain(html_doc, stages)
    
    if chain_result.success:
        print(f"Final content: {chain_result.content}")
        print(f"Total elapsed time: {chain_result.elapsed_time:.2f}s")
        print(f"Final token size: {chain_result.filtered_data_token_size}")
        print(f"Stages completed: {len(chain_result.stages_config)}")
        
        # Print stage info
        for i, (extraction_spec, filter_strategy) in enumerate(chain_result.stages_config):
            spec_names = [spec.name for spec in extraction_spec]
            print(f"Stage {i+1}: {spec_names} using '{filter_strategy}' strategy")
        
        # Print individual stage results
        for i, filter_op in enumerate(chain_result.filterops):
            status = "✅" if filter_op.success else "❌"
            print(f"Stage {i+1} {status}: {len(filter_op.content) if filter_op.content else 0} chars, {filter_op.elapsed_time:.2f}s")
            print("Content: ")
            print(" ")
            print(filter_op.content)
            print(" ")
            print(" ")
            print(" ")


        # Print reduction details
        for i, reduction in enumerate(chain_result.reduction_details):
            reduction_percent = (1 - reduction["filtered_token_size"] / reduction["source_token_size"]) * 100
            print(f"Stage {i+1}: {reduction['source_token_size']} → {reduction['filtered_token_size']} tokens ({reduction_percent:.1f}% reduction)")
            
        # Print total cost
        if chain_result.usage and "total_cost" in chain_result.usage:
            print(f"Total cost: ${chain_result.usage['total_cost']:.4f}")
    else:
        print(f"Chain failed: {chain_result.error}")




wrt_to_source_filter_desc="""
### Task
Return **every content chunk** that is relevant to the main product
described in the page’s hero section.

### How to decide relevance
1. **Keep** a chunk if its title, brand, or descriptive text
   • matches the hero product **or**
   • is ambiguous / generic enough that it _could_ be the hero product.
2. **Discard** a chunk **only when** there is a **strong, explicit** signal
   that it belongs to a _different_ item (e.g. totally different brand,
   unrelated product type, “customers also bought” label).
3. When in doubt, **keep** the chunk (favor recall).

### Output
Return the retained chunks exactly as HTML snippets.
""".strip()



# ─────────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":


    example_chain_usage()

   
    # cfg = ExtractConfig()
    # filter_hero = FilterHero(cfg)
    
   
    # html_doc1 = """
    # <html><body>
    #   <div class="product"><h2 class="title">Wireless Keyboard</h2><span class="price">€49.99</span></div>
    #   <div class="product"><h2 class="title">USB-C Hub</h2><span class="price">€29.50</span></div>
    # </body></html>
    # """
    # html_doc2 = load_html("extracthero/simple_html_sample_2.html")
    # html_doc3 = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    

    
    # specs = [
    #     WhatToRetain(
    #         name="product titles",
    #         desc="listing name of prodct",
    #         include_context_chunk=False,
    #     )
       
    # ]


    # #filter_op = filter_hero.run(html_doc1, specs, filter_strategy="recall")

    
    # # stages = [
    # #     ([WhatToRetain(name="voltage", desc="all voltage info")], "contextual"),
    # #     ([WhatToRetain(name="precise_voltage", desc="only voltage values")], "inclusive"),
    # # ]
    
    # stages_config = [
    #     (specs, "contextual"),
    #     (specs, "inclusive"),
    # ]


 
    
    # filter_ops = filter_hero.chain(html_doc3, stages)

    
    
    
    # print("cost: ", filter_op.usage["total_cost"])

    
    # # print("")
    # # # print("prompt: ", filter_op.generation_result.generation_request.formatted_prompt)

   



    
    # print("filter_strategy:", filter_op.filter_strategy)
    
    # print("Filtered corpus: ⬇")
    # print(" ")
    # print(filter_op.content)
    
    # print(" ")
    # # print(filter_op.start_time)

    
