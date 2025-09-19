# myllmservice.py - Updated for Responses API with Structured Outputs

import logging
import asyncio
from llmservice.base_service import BaseLLMService
from llmservice.generation_engine import GenerationRequest, GenerationResult
from typing import Optional, Union, List, Dict, Any
import json
from extracthero import prompts
from pydantic import BaseModel, Field


# ============================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================

class ParsedContent(BaseModel):
    """Schema for parsed content output."""
    extracted_data: Dict[str, Any] = Field(default_factory=dict, description="Extracted structured data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score")


class FilteredContent(BaseModel):
    """Schema for filtered content output."""
    filtered_text: str = Field(default="", description="The filtered content")
    items_removed: Optional[int] = Field(default=None, description="Number of items removed")
    filter_strategy_used: Optional[str] = Field(default=None, description="Strategy applied")


class TocSection(BaseModel):
    """Schema for a document section in Table of Contents."""
    name: str = Field(description="Name/title of the section")
    category: str = Field(
        description="Type of content: navigation, content, metadata, code, footer, or header"
    )
    start_line: int = Field(description="Starting line number (inclusive)", ge=1)
    end_line: int = Field(description="Ending line number (inclusive)", ge=1)
    is_content: bool = Field(
        description="Whether this section contains relevant content based on what_to_retain"
    )
    is_navigation: bool = Field(
        description="Whether this section is primarily navigation links"
    )


class TocOutput(BaseModel):
    """Schema for Table of Contents output."""
    sections: List[TocSection] = Field(
        description="List of document sections with their properties"
    )
    
    def display(self) -> str:
        """
        Return a formatted string representation showing all sections in JSON-like format.
        """
        lines = []
        lines.append("{")
        lines.append(f'  "sections": [')
        
        for i, section in enumerate(self.sections):
            lines.append("    {")
            lines.append(f'      "name": "{section.name}",')
            lines.append(f'      "category": "{section.category}",')
            lines.append(f'      "start_line": {section.start_line},')
            lines.append(f'      "end_line": {section.end_line},')
            lines.append(f'      "is_content": {str(section.is_content).lower()},')
            lines.append(f'      "is_navigation": {str(section.is_navigation).lower()}')
            
            if i < len(self.sections) - 1:
                lines.append("    },")
            else:
                lines.append("    }")
        
        lines.append("  ]")
        lines.append("}")
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """Default string representation shows all sections."""
        return self.display()
    
    def __repr__(self) -> str:
        """Developer representation shows model details."""
        return f"TocOutput(sections={len(self.sections)} items)"


# Update forward reference for nested model
TocSection.model_rebuild()


class DeletionIndices(BaseModel):
    """Schema for line deletion operations."""
    deletions: Optional[List[Dict[str, int]]] = Field(
        default=None,
        description="List of line ranges to delete, each with 'start' and 'end' keys"
    )
    total_lines_to_delete: Optional[int] = Field(default=0, description="Total number of lines to delete")
    reasoning: Optional[str] = Field(default=None, description="Reasoning for deletions")


class CategoryResult(BaseModel):
    """Schema for categorization results."""
    category: str = Field(default="", description="The identified category")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence in the categorization")
    reasoning: str = Field(default="", description="Brief explanation of the categorization")


class AnalysisResult(BaseModel):
    """Schema for analysis results."""
    summary: str = Field(default="", description="Summary of the analysis")
    key_findings: List[str] = Field(default_factory=list, description="Key findings from the analysis")
    recommendations: Optional[List[str]] = Field(default=None, description="Recommendations")
    confidence_score: float = Field(default=0.5, ge=0, le=1, description="Overall confidence")






# ============================================================
# SERVICE IMPLEMENTATION
# ============================================================

class MyLLMService(BaseLLMService):
    def __init__(self, logger=None, max_concurrent_requests=200):
        super().__init__(
            logger=logging.getLogger(__name__),
            default_model_name="gpt-4o-mini",  # Updated from gpt-4.1-nano
            max_rpm=500,
            max_concurrent_requests=max_concurrent_requests,
        )

    def parse_via_llm(
        self,
        corpus: str,
        parse_keywords=None,
        model=None,
        content_output_format="json"
    ) -> GenerationResult:
        """
        Parse content using structured outputs instead of pipelines.
        """
        user_prompt = None

        if content_output_format == "json":
            user_prompt = prompts.PARSE_2_JSON_VIA_LLM_PROMPT.format(
                corpus=corpus,
                parse_keywords=parse_keywords,
            )
            # Use structured output schema
            response_schema = ParsedContent
            
        elif content_output_format in ["markdown", "text"]:
            user_prompt = prompts.PARSE_2_MARKDOWN_VIA_LLM_PROMPT.format(
                corpus=corpus,
                parse_keywords=parse_keywords,
                content_output_format=content_output_format
            )
            # For markdown/text, use raw output
            response_schema = None

        if model is None:
            model = "gpt-4o-mini"

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=response_schema if content_output_format == "json" else None,
            operation_name="parse_via_llm",
        )

        result = self.execute_generation(generation_request)
        
        # If using structured output, parse the JSON
        if result.success and content_output_format == "json" and response_schema:
            try:
                data = json.loads(result.content)
                parsed = ParsedContent(**data)
                # Convert back to dict for backward compatibility
                result.content = parsed.extracted_data
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse structured output: {e}")
        
        return result

    def analyze_individual_filter_prompt_experiment(self, experiment_data, model=None) -> GenerationResult:
        """
        Analyze filter experiments using structured outputs.
        """
        experiment_data = json.dumps(experiment_data, indent=2)

        user_prompt = prompts.PROMPT_analyze_individual_filter_prompt_experiment.format(
            experiment_data=experiment_data,
        )

        if model is None:
            model = "gpt-4o-mini"  # Updated from o3

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=AnalysisResult,
            operation_name="analyze_filter_experiment",
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output if successful
        if result.success:
            try:
                data = json.loads(result.content)
                analysis = AnalysisResult(**data)
                # Format for backward compatibility
                result.content = f"Summary: {analysis.summary}\n\nKey Findings:\n" + \
                               "\n".join(f"- {f}" for f in analysis.key_findings)
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse analysis: {e}")
        
        return result

    def analyze_filter_prompt_experiment_overall(self, merged_individual_results, model=None) -> GenerationResult:
        """
        Analyze overall filter experiments using structured outputs.
        """
        user_prompt = prompts.PROMPT_analyze_filter_prompt_experiment_overall.format(
            merged_individual_results=merged_individual_results,
        )

        if model is None:
            model = "gpt-4o-mini"  # Updated from o3

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=AnalysisResult,
            operation_name="analyze_overall_experiment",
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output if successful
        if result.success:
            try:
                data = json.loads(result.content)
                analysis = AnalysisResult(**data)
                # Format for backward compatibility
                result.content = f"Summary: {analysis.summary}\n\nKey Findings:\n" + \
                               "\n".join(f"- {f}" for f in analysis.key_findings)
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse analysis: {e}")
        
        return result

    def filter_via_llm(
        self,
        corpus: str,
        thing_to_extract,
        model=None,
        filter_strategy=None
    ) -> GenerationResult:
        """
        Filter content using structured outputs for better reliability.
        """
        # Select prompt based on strategy
        if filter_strategy == "relaxed":
            user_prompt = prompts.PROPMT_filter_via_llm_RELAXED.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "focused":
            user_prompt = prompts.PROPMT_filter_via_llm_FOCUSED.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "contextual":
            user_prompt = prompts.PROPMT_filter_via_llm_contextual.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "preserve":
            user_prompt = prompts.PROPMT_filter_via_llm_PRESERVE.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "strict":
            user_prompt = prompts.PROPMT_filter_via_llm_STRICT.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        else:
            # Default to strict
            user_prompt = prompts.PROPMT_filter_via_llm_STRICT.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )

        if model is None:
            model = "gpt-4o-mini"

        # For filtering, we typically want raw text output
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=None,  # Raw text output for filters
            operation_name="filter_via_llm",
        )

        result = self.execute_generation(generation_request)
        return result
    




    def get_content_toc(
        self,
        numbered_corpus,
        max_line, 
        what_to_retain,
        model: Optional[str] = None,
    ) -> GenerationResult:
       
        
        if model is None:
            model = "gpt-4.1-mini"

        
        user_prompt = prompts.TOC.format( numbered_corpus=numbered_corpus,
                                          max_line=max_line,
                                          what_to_retain=what_to_retain)
        
        # len(original_lines)
        
        # Use structured output for ToC
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=TocOutput,  # Use TocOutput schema
            operation_name="get_content_toc",
            verbosity="medium"
        )

       
        
        result = self.execute_generation(generation_request)
        
        # Parse structured output and keep as TocOutput for proper handling
        if result.success:
            try:
                # The content should already be parsed by the generation engine
                # Just validate it's the right type
                if isinstance(result.content, str):
                    data = json.loads(result.content)
                    toc_output = TocOutput(**data)
                    result.content = toc_output  # Keep as TocOutput object
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse ToC output: {e}")
                # Try to recover if possible
                result.success = False
                result.error_message = f"Failed to parse structured output: {e}"
        
        return result

    def get_deletions_via_llm(
        self,
        numbered_corpus: str,
        thing_to_extract: str,
        model: Optional[str] = None,
        filter_strategy: str = "relaxed"
    ) -> GenerationResult:
        """
        Get line deletion indices using structured outputs.
        """
        # Select appropriate prompt based on strategy
        if filter_strategy == "relaxed":
            user_prompt = prompts.SUBTRACTIVE_FILTER_RELAXED.format(
                numbered_corpus=numbered_corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "contextual":
            user_prompt = prompts.SUBTRACTIVE_FILTER_CONTEXTUAL.format(
                numbered_corpus=numbered_corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "focused":
            user_prompt = prompts.SUBTRACTIVE_FILTER_FOCUSED.format(
                numbered_corpus=numbered_corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "preserve":
            user_prompt = prompts.SUBTRACTIVE_FILTER_PRESERVE.format(
                numbered_corpus=numbered_corpus,
                thing_to_extract=thing_to_extract
            )
        else:  # strict or default
            user_prompt = prompts.SUBTRACTIVE_FILTER_STRICT.format(
                numbered_corpus=numbered_corpus,
                thing_to_extract=thing_to_extract
            )

        if model is None:
            model = "gpt-4o-mini"

        # Use structured output for deletion indices
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=DeletionIndices,
            operation_name="get_deletions_via_llm",
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output and convert to dict for backward compatibility
        if result.success:
            try:
                data = json.loads(result.content)
                deletion_info = DeletionIndices(**data)
                # Convert to dict format expected by existing code
                result.content = {
                    "deletions": deletion_info.deletions or [],
                    "total_lines_to_delete": deletion_info.total_lines_to_delete or 0,
                    "reasoning": deletion_info.reasoning
                }
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse deletion indices: {e}")
                # Fallback to attempting direct dict conversion
                try:
                    result.content = json.loads(result.content)
                except:
                    pass
        
        return result
    

    def get_deletions_via_llm_custom_with_schema(
        self,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> GenerationResult:
        """
        Get Table of Contents with custom prompt using structured outputs.
        
        Parameters:
        -----------
        user_prompt : str
            The prompt to send to the LLM
        model : Optional[str]
            Model to use, defaults to gpt-4o-mini
        """
        if model is None:
            model = "gpt-4o-mini"

        # Use structured output for ToC
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=TocOutput,  # Use TocOutput schema
            operation_name="get_deletions_via_llm_custom_with_schema",
            verbosity="medium"
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output and keep as TocOutput for proper handling
        if result.success:
            try:
                # The content should already be parsed by the generation engine
                # Just validate it's the right type
                if isinstance(result.content, str):
                    data = json.loads(result.content)
                    toc_output = TocOutput(**data)
                    result.content = toc_output  # Keep as TocOutput object
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse ToC output: {e}")
                # Try to recover if possible
                result.success = False
                result.error_message = f"Failed to parse structured output: {e}"
        
        return result
    
    def get_deletions_via_llm_custom(
        self,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> GenerationResult:
        """
        Get line deletion indices with custom prompt using structured outputs.
        """
        if model is None:
            model = "gpt-4o-mini"

        # Use structured output for deletion indices
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
           # response_schema=DeletionIndices,
            operation_name="get_deletions_via_llm_custom",
            # reasoning_effort="low",
            verbosity= "medium"
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output and convert to dict for backward compatibility
        if result.success:
            try:
                data = json.loads(result.content)
                deletion_info = DeletionIndices(**data)
                # Convert to dict format expected by existing code
                result.content = {
                    "deletions": deletion_info.deletions or [],
                    "total_lines_to_delete": deletion_info.total_lines_to_delete or 0,
                    "reasoning": deletion_info.reasoning
                }
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse deletion indices: {e}")
                # Fallback to attempting direct dict conversion
                try:
                    result.content = json.loads(result.content)
                except:
                    pass
        
        return result

    # ============================================================
    # ASYNC METHODS
    # ============================================================

    async def filter_via_llm_async(
        self,
        corpus: str,
        thing_to_extract,
        model=None,
        filter_strategy=None
    ) -> GenerationResult:
        """
        Async version of filter_via_llm using structured outputs.
        """
        # Select prompt based on strategy
        if filter_strategy == "relaxed":
            user_prompt = prompts.PROPMT_filter_via_llm_RELAXED.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "focused":
            user_prompt = prompts.PROPMT_filter_via_llm_FOCUSED.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "contextual":
            user_prompt = prompts.PROPMT_filter_via_llm_contextual.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        elif filter_strategy == "preserve":
            user_prompt = prompts.PROPMT_filter_via_llm_PRESERVE.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )
        else:
            user_prompt = prompts.PROPMT_filter_via_llm_STRICT.format(
                corpus=corpus,
                thing_to_extract=thing_to_extract
            )

        if model is None:
            model = "gpt-4o-mini"

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=None,  # Raw text output for filters
            operation_name="filter_via_llm_async",
        )

        # Use async execution
        result = await self.execute_generation_async(generation_request)
        return result

    async def parse_via_llm_async(
        self,
        corpus: str,
        parse_keywords: List[str] | None = None,
        model: str | None = None,
        content_output_format="json"
    ) -> GenerationResult:
        """
        Async version of parse_via_llm using structured outputs.
        """
        user_prompt = None

        if content_output_format == "json":
            user_prompt = prompts.PARSE_2_JSON_VIA_LLM_PROMPT.format(
                corpus=corpus,
                parse_keywords=parse_keywords,
            )
            # Use structured output schema
            response_schema = ParsedContent
            
        elif content_output_format in ["markdown", "text"]:
            user_prompt = prompts.PARSE_2_MARKDOWN_VIA_LLM_PROMPT.format(
                corpus=corpus,
                parse_keywords=parse_keywords,
                content_output_format=content_output_format
            )
            # For markdown/text, use raw output
            response_schema = None

        if model is None:
            model = "gpt-4o-mini"

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            response_schema=response_schema if content_output_format == "json" else None,
            operation_name="parse_via_llm_async",
        )

        result = await self.execute_generation_async(generation_request)
        
        # If using structured output, parse the JSON
        if result.success and content_output_format == "json" and response_schema:
            try:
                data = json.loads(result.content)
                parsed = ParsedContent(**data)
                # Convert back to dict for backward compatibility
                result.content = parsed.extracted_data
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse structured output: {e}")
        
        return result

    async def dummy_categorize_simple_async(self) -> GenerationResult:
        """
        Categorization example using structured outputs instead of SemanticIsolation pipeline.
        """
        user_prompt = """Here is list of classes: Food & Dining
                                                        Utilities
                                                        Accommodation
                                                        Incoming P2P Transfer
                                                        Outgoing P2P Transfers
                                                        Cash Withdrawal
                                                        Cash Deposit
                                                        Healthcare
                                                        Leisure and Activities in Real Life
                                                        Retail Purchases
                                                        Personal Care
                                                        Online Subscriptions & Services,
        

                            and here is string record to be classified:

                            pharmacy - eczane 30 dollars 28.05.24

                            Task Description:
                            Identify the Category: Determine which of the categories the string belongs to.
                            Extra Information - Helpers:  There might be additional information under each subcategory labeled as 'helpers'. These helpers include descs for the taxonomy,  but
                            should be considered as extra information and not directly involved in the classification task
                            Instructions:
                            Given the string record, first identify the category of the given string using given category list,  (your final answer shouldn't include words like "likely").
                            Use the 'Helpers' section for additional context.  And also at the end explain your reasoning in a very short way. 
                            Make sure category is selected from given categories and matches 100%
                            Examples:
                            Record: "Jumper Cable"
                            lvl1: interconnectors
                            
                            Record: "STM32"
                            lvl1: microcontrollers
        """

        # Use structured output for categorization
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model="gpt-4o-mini",
            response_schema=CategoryResult,
            operation_name="categorize_simple_async",
        )

        result = await self.execute_generation_async(generation_request)
        
        # Parse structured output
        if result.success:
            try:
                data = json.loads(result.content)
                category_result = CategoryResult(**data)
                # Format for backward compatibility
                result.content = category_result.category
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse category: {e}")
        
        return result

    def dummy_categorize_simple(self) -> GenerationResult:
        """
        Synchronous categorization using structured outputs instead of SemanticIsolation pipeline.
        """
        formatted_prompt = """Here is list of classes: Food & Dining
                                                        Utilities
                                                        Accommodation
                                                        Incoming P2P Transfer
                                                        Outgoing P2P Transfers
                                                        Cash Withdrawal
                                                        Cash Deposit
                                                        Healthcare
                                                        Leisure and Activities in Real Life
                                                        Retail Purchases
                                                        Personal Care
                                                        Online Subscriptions & Services,
        
                            and here is string record to be classified:  
                            
                            pharmacy - eczane 30 dollars 28.05.24

                            Task Description:
                            Identify the Category: Determine which of the categories the string belongs to.
                            Extra Information - Helpers:  There might be additional information under each subcategory labeled as 'helpers'. These helpers include descs for the taxonomy,  but
                            should be considered as extra information and not directly involved in the classification task
                            Instructions:
                            Given the string record, first identify the category of the given string using given category list,  (your final answer shouldnt include words like "likely").
                            Use the 'Helpers' section for additional context.  And also at the end explain your reasoning in a very short way. 
                            Make sure category is selected from given categories and matches 100%
                            Examples:
                            Record: "Jumper Cable"
                            lvl1: interconnectors
                            
                            Record: "STM32"
                            lvl1: microcontrollers
                             """

        # Use structured output for categorization
        generation_request = GenerationRequest(
            user_prompt=formatted_prompt,
            model="gpt-4o-mini",
            response_schema=CategoryResult,
            operation_name="categorize_simple",
        )

        result = self.execute_generation(generation_request)
        
        # Parse structured output
        if result.success:
            try:
                data = json.loads(result.content)
                category_result = CategoryResult(**data)
                # Format for backward compatibility
                result.content = category_result.category
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse category: {e}")
        
        return result


def main():
    """
    Main function to test the categorize_simple method of MyLLMService.
    """
    # Initialize the service
    my_llm_service = MyLLMService()

    # Test dummy categorization
    try:
        result = my_llm_service.dummy_categorize_simple()

        # Print the result
        print("Generation Result:", result)
        if result.success:
            print("Categorized Content:", result.content)
        else:
            print("Error:", result.error_message)
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == "__main__":
    main()