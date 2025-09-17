"""
LLM Factory - 통합 LLM 팩토리 라이브러리

이 라이브러리는 다양한 LLM 제공자(OpenAI, Azure OpenAI, Anthropic, Ollama)를
통합된 인터페이스로 사용할 수 있게 해주는 팩토리 패턴 라이브러리입니다.
"""

from .factory import (
    LLMFactory,
    create_llm,
    create_openai_llm,
    create_azure_llm,
    create_anthropic_llm,
    create_ollama_llm,
    create_embedding,
    create_openai_embedding,
    create_azure_embedding,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "LLMFactory",
    "create_llm",
    "create_openai_llm",
    "create_azure_llm", 
    "create_anthropic_llm",
    "create_ollama_llm",
    "create_embedding",
    "create_openai_embedding",
    "create_azure_embedding",
]
