"""
LangChain-based tools for LLM interaction and structured data extraction.
"""

import logging
import traceback
from typing import Type, TypeVar, Optional, Dict
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..auth.tokens import get_revos_token, invalidate_revos_token
from ..config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class LangChainExtractor:
    """Extracts structured data using LangChain and LLM."""
    
    def __init__(self, model_name: str, settings_instance=None, name=None):
        if not model_name:
            raise ValueError("model_name is required to instantiate LangChainExtractor")
        
        self.settings = settings_instance or get_settings()
        self.model_name = model_name
        self.name = name or f"extractor_{model_name}"
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM client."""
        try:
            # Get token from Revos
            token = get_revos_token()
            
            # Get LLM configuration
            if self.model_name and hasattr(self.settings, 'llm_models'):
                # Use specific model from multiple models configuration
                llm_config = self.settings.llm_models.get_model(self.model_name)
            else:
                # Use default single LLM configuration
                llm_config = self.settings.llm
            
            revo_config = self.settings.revo
            
            self.llm = ChatOpenAI(
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                top_p=llm_config.top_p,
                frequency_penalty=llm_config.frequency_penalty,
                presence_penalty=llm_config.presence_penalty,
                api_key=token,
                base_url=revo_config.base_url
            )
            logger.info("LangChain LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain LLM: {e}")
            logger.debug(f"LLM initialization traceback: {traceback.format_exc()}")
            # If token acquisition fails, don't create the extractor at all
            raise RuntimeError(f"Cannot initialize LangChainExtractor: {e}") from e
    
    def _refresh_llm(self, use_fallback: bool = False):
        """Refresh LLM with new token"""
        logger.info(f"Refreshing LLM with new token (fallback={use_fallback})...")
        
        try:
            invalidate_revos_token()
            token = get_revos_token(force_refresh=True, use_fallback=use_fallback)
            
            llm_config = self.settings.llm
            revo_config = self.settings.revo
            
            self.llm = ChatOpenAI(
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                top_p=llm_config.top_p,
                frequency_penalty=llm_config.frequency_penalty,
                presence_penalty=llm_config.presence_penalty,
                api_key=token,
                base_url=revo_config.base_url
            )
            logger.info("LLM refresh successful")
        except Exception as e:
            logger.error(f"LLM refresh failed: {str(e)}")
            logger.error(f"LLM refresh traceback: {traceback.format_exc()}")
            self.llm = None
    
    async def extract(self, target: Type[T], prompt: PromptTemplate, **kwargs) -> T:
        """Extract structured data using LLM."""
        if not self.llm:
            raise RuntimeError("LLM not available. Cannot perform extraction.")
        
        try:
            # Create output parser
            parser = PydanticOutputParser(pydantic_object=target)
            
            # Format the prompt
            format_instructions = parser.get_format_instructions()
            
            # Create the final prompt template with proper variable handling
            # Remove format_instructions from input_variables to avoid overlap with partial_variables
            input_variables = [var for var in prompt.input_variables if var != 'format_instructions']
            
            # Create partial variables dict, ensuring format_instructions is included
            partial_vars = dict(prompt.partial_variables)
            partial_vars['format_instructions'] = format_instructions
            
            final_prompt = PromptTemplate(
                input_variables=input_variables,
                template=prompt.template,
                partial_variables=partial_vars
            )
            
            # Format the prompt with provided data
            formatted_prompt = final_prompt.format(**kwargs)
            
            # Get LLM response
            messages = [HumanMessage(content=formatted_prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Parse the response
            result = parser.parse(response.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            logger.error(f"LLM extraction traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to extract structured data: {e}") from e
    
    def extract_structured_data(self, prompt: str, target_class: Type[T], **kwargs) -> T:
        """
        Extract structured data from a prompt using the target class.
        
        Args:
            prompt: The prompt text to process
            target_class: The Pydantic model class to extract data into
            **kwargs: Additional arguments to pass to the extract method
            
        Returns:
            T: Instance of target_class with extracted data
        """
        # Create a simple prompt template
        prompt_template = PromptTemplate(
            input_variables=[],
            template=prompt
        )
        
        # Use the async extract method synchronously
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we need to handle this differently
                # For now, we'll use a simple approach
                return self._extract_sync(prompt_template, target_class, **kwargs)
            else:
                return loop.run_until_complete(self.extract(target_class, prompt_template, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.extract(target_class, prompt_template, **kwargs))
    
    def _extract_sync(self, prompt_template: PromptTemplate, target_class: Type[T], **kwargs) -> T:
        """Synchronous extraction fallback."""
        if not self.llm:
            raise RuntimeError("LLM not available. Cannot perform extraction.")
        
        try:
            # Create output parser
            parser = PydanticOutputParser(pydantic_object=target_class)
            
            # Format the prompt
            format_instructions = parser.get_format_instructions()
            
            # Create the final prompt template with proper variable handling
            input_variables = [var for var in prompt_template.input_variables if var != 'format_instructions']
            
            # Create partial variables dict, ensuring format_instructions is included
            partial_vars = dict(prompt_template.partial_variables)
            partial_vars['format_instructions'] = format_instructions
            
            final_prompt = PromptTemplate(
                input_variables=input_variables,
                template=prompt_template.template,
                partial_variables=partial_vars
            )
            
            # Format the prompt
            formatted_prompt = final_prompt.format(**kwargs)
            
            # Create message
            message = HumanMessage(content=formatted_prompt)
            
            # Get response from LLM
            response = self.llm.invoke([message])
            
            # Parse the response
            result = parser.parse(response.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            logger.error(f"LLM extraction traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to extract structured data: {e}") from e
    
    def get_current_model(self) -> str:
        """
        Get the name of the currently active model.
        
        Returns:
            str: Name of the current model
        """
        return self.model_name


# Global extractor instances (lazy initialization)
_langchain_extractors: Dict[str, LangChainExtractor] = {}


def get_langchain_extractor(model_name: str) -> LangChainExtractor:
    """
    Get a LangChain extractor instance for a specific model.
    
    Args:
        model_name: Name of the model to use.
        
    Returns:
        LangChainExtractor: Extractor instance for the specified model
        
    Raises:
        ValueError: If model_name is not provided
    """
    if not model_name:
        raise ValueError("model_name is required to get LangChainExtractor")
    
    global _langchain_extractors
    
    # Create extractor if it doesn't exist
    if model_name not in _langchain_extractors:
        _langchain_extractors[model_name] = LangChainExtractor(model_name=model_name)
    
    return _langchain_extractors[model_name]


def create_all_extractors(settings_instance=None) -> Dict[str, LangChainExtractor]:
    """
    Create extractor instances for all available models.
    
    Args:
        settings_instance: Optional settings instance to use
        
    Returns:
        Dict[str, LangChainExtractor]: Dictionary mapping model names to extractor instances
        
    Raises:
        ValueError: If no models are configured
    """
    settings = settings_instance or get_settings()
    extractors = {}
    
    if hasattr(settings, 'llm_models') and settings.llm_models.models:
        # Create extractors for all available models
        for model_name in settings.llm_models.list_available_models().keys():
            extractors[model_name] = LangChainExtractor(
                model_name=model_name,
                settings_instance=settings,
                name=f"extractor_{model_name}"
            )
    else:
        raise ValueError("No models configured. Please configure models in llm_models.models or use get_langchain_extractor() with a specific model name.")
    
    return extractors


def list_available_extractors(settings_instance=None) -> Dict[str, str]:
    """
    List all available extractor instances.
    
    Args:
        settings_instance: Optional settings instance to use
    
    Returns:
        Dict[str, str]: Dictionary mapping extractor names to model descriptions
        
    Raises:
        ValueError: If no models are configured
    """
    settings = settings_instance or get_settings()
    
    if hasattr(settings, 'llm_models') and settings.llm_models.models:
        return settings.llm_models.list_available_models()
    else:
        raise ValueError("No models configured. Please configure models in llm_models.models.")


