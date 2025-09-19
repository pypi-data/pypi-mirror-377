# extracthero/filter_engine.py
"""
FilterEngine - Core filtering logic used by FilterHero.
Handles LLM dispatch, pipeline execution, and result aggregation.

python -m extracthero.filter_engine
"""

from __future__ import annotations

import json as _json
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio

from llmservice import GenerationResult
from extracthero.myllmservice import MyLLMService
from extracthero.schemas import WhatToRetain
from extracthero.utils import load_html




class FilterEngine:
    """
    Core filtering engine that handles LLM dispatch and multi-stage pipelines.
    Used by FilterHero as the execution engine.
    """
    
    def __init__(self, llm_service: Optional[MyLLMService] = None):
        self.llm = llm_service or MyLLMService()
    
 

    def execute_filtering(
        self,
        corpus: str,
        extraction_spec: Union[WhatToRetain, List[WhatToRetain], str],
        strategy: str,
        model_name: Optional[str] = None
    ) -> GenerationResult:
        
        if isinstance(extraction_spec, WhatToRetain):
            # Use the compile method from WhatToRetain
            target_desc = extraction_spec.compile()
        elif isinstance(extraction_spec, str):
            target_desc = extraction_spec
        else:
            # Handle list of WhatToRetain specs - compile each one
            compiled_specs = [spec.compile() for spec in extraction_spec]
            target_desc = "\n\n".join(compiled_specs)
        
        gen_results = self.llm.filter_via_llm(
                corpus, 
                target_desc, 
                filter_strategy=strategy,
                model=model_name
            )
        
        return gen_results
    
    def execute_subtractive_filtering(
        self,
        numbered_corpus: str,
        extraction_spec: Union[WhatToRetain, List[WhatToRetain]],
        strategy: str,
        model_name: Optional[str] = None
    ) -> GenerationResult:
        """
        Execute subtractive filtering using ToC approach.
        
        This uses Semantic Section Mapping to identify document sections
        and determine which to keep based on extraction spec.
        """
        
        if isinstance(extraction_spec, WhatToRetain):
            # Use the compile method from WhatToRetain
            target_desc = extraction_spec.compile()
        elif isinstance(extraction_spec, str):
            target_desc=extraction_spec
        else:
            # Handle list of WhatToRetain specs - compile each one
            compiled_specs = [spec.compile() for spec in extraction_spec]
            target_desc = "\n\n".join(compiled_specs)
        
        # Count lines in numbered_corpus
        max_line = len(numbered_corpus.split('\n'))
        
        # Use ToC-based content identification via LLM
        gen_results = self.llm.get_content_toc(
            numbered_corpus=numbered_corpus,
            max_line=max_line,
            what_to_retain=target_desc,
            model=model_name
        )
        
        return gen_results
    
    
    async def execute_filtering_async(
        self,
        corpus: str,
        extraction_spec: Union[WhatToRetain, List[WhatToRetain], str],
        strategy: str,
        model_name: Optional[str] = None
    ) -> GenerationResult:
        
        if isinstance(extraction_spec, WhatToRetain):
            # Use the compile method from WhatToRetain
            target_desc = extraction_spec.compile()
        elif isinstance(extraction_spec, str):
            target_desc = extraction_spec
        else:
            # Handle list of WhatToRetain specs - compile each one
            compiled_specs = [spec.compile() for spec in extraction_spec]
            target_desc = "\n\n".join(compiled_specs)
        
        gen_results = await self.llm.filter_via_llm_async(
                corpus, 
                target_desc, 
                filter_strategy=strategy,
                model=model_name
            )
        
        return gen_results
        
       
    



# ─────────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":
    filter_engine=FilterEngine()
   
    specs = [
        WhatToRetain(
            name="name",
            desc="all information about name",
            include_context_chunk=False,
        )
    ]
    
    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    dummy_sample="""
    New york is too hot
     
    My name is Enes"""

    gen_results=filter_engine.execute_filtering(dummy_sample,
                                    extraction_spec=specs, 
                                    strategy="relaxed", 
                                    model_name="gpt-4o-mini" )
    
   

    print(gen_results.content)
    
    
    