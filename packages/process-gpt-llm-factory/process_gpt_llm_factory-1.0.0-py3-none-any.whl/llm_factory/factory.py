"""
공통 LLM 팩토리 라이브러리
각 마이크로서비스에서 사용할 수 있는 통합 LLM 팩토리
"""
import os
from typing import Optional, Any, Dict
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.language_models.base import BaseLanguageModel


class LLMFactory:
    """LLM 팩토리 클래스 - 환경변수에 따라 적절한 LLM 인스턴스를 생성"""
    
    @staticmethod
    def create_llm(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        streaming: bool = True,
        **kwargs
    ) -> BaseLanguageModel:
        """
        LLM 인스턴스를 생성합니다.
        
        Args:
            provider: LLM 제공자 (openai, azure, anthropic, ollama)
            model: 모델명 (제공자별 기본값 사용)
            temperature: 온도 설정
            streaming: 스트리밍 사용 여부
            **kwargs: 추가 설정 파라미터
            
        Returns:
            BaseLanguageModel: 생성된 LLM 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 제공자일 경우
        """
        # 환경변수에서 제공자와 모델 정보 가져오기
        provider = provider or os.getenv("LLM_PROVIDER", "openai")
        model = model or LLMFactory._get_default_model(provider)
        
        # 제공자별 LLM 생성
        if provider == "openai":
            return LLMFactory._create_openai_llm(model, temperature, streaming, **kwargs)
        elif provider == "azure":
            return LLMFactory._create_azure_llm(model, temperature, streaming, **kwargs)
        elif provider == "anthropic":
            return LLMFactory._create_anthropic_llm(model, temperature, streaming, **kwargs)
        elif provider == "ollama":
            return LLMFactory._create_ollama_llm(model, temperature, streaming, **kwargs)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")
    
    @staticmethod
    def _get_default_model(provider: str) -> str:
        """제공자별 기본 모델명 반환"""
        defaults = {
            "openai": "gpt-4o",
            "azure": "gpt-4.1-mini",
            "anthropic": "claude-3-sonnet-20240229",
            "ollama": "llama3"
        }
        return defaults.get(provider, "gpt-4o")
    
    @staticmethod
    def _get_default_embedding_model(provider: str) -> str:
        """제공자별 기본 embedding 모델명 반환"""
        defaults = {
            "openai": "text-embedding-3-large",
            "azure": "text-embedding-3-large",
            "anthropic": "text-embedding-3-large",  # OpenAI 사용
            "ollama": "text-embedding-3-large"      # OpenAI 사용
        }
        return defaults.get(provider, "text-embedding-3-large")
    
    @staticmethod
    def _create_openai_llm(model: str, temperature: float, streaming: bool, **kwargs) -> ChatOpenAI:
        """OpenAI LLM 생성"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
            **kwargs
        )
    
    @staticmethod
    def _create_azure_llm(model: str, temperature: float, streaming: bool, **kwargs) -> AzureChatOpenAI:
        """Azure OpenAI LLM 생성"""
        api_key = os.getenv("AZURE_API_KEY")
        endpoint = os.getenv("AZURE_ENDPOINT")
        deployment = os.getenv("AZURE_DEPLOYMENT")
        
        if not all([api_key, endpoint, deployment]):
            raise ValueError("Azure OpenAI 설정이 완전하지 않습니다. AZURE_API_KEY, AZURE_ENDPOINT, AZURE_DEPLOYMENT를 확인하세요.")
        
        return AzureChatOpenAI(
            deployment_name=deployment,
            model=model,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=os.getenv("AZURE_API_VERSION", "2024-06-01-preview"),
            temperature=temperature,
            streaming=streaming,
            **kwargs
        )
    
    @staticmethod
    def _create_anthropic_llm(model: str, temperature: float, streaming: bool, **kwargs) -> ChatAnthropic:
        """Anthropic LLM 생성"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        
        return ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
            **kwargs
        )
    
    @staticmethod
    def _create_ollama_llm(model: str, temperature: float, streaming: bool, **kwargs) -> ChatOllama:
        """Ollama LLM 생성"""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            **kwargs
        )
    
    @staticmethod
    def _create_openai_embedding(model: str, **kwargs) -> OpenAIEmbeddings:
        """OpenAI Embedding 생성"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        return OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def _create_azure_embedding(model: str, **kwargs) -> AzureOpenAIEmbeddings:
        """Azure OpenAI Embedding 생성"""
        api_key = os.getenv("AZURE_API_KEY")
        endpoint = os.getenv("AZURE_ENDPOINT")
        
        if not all([api_key, endpoint]):
            raise ValueError("Azure OpenAI embedding 설정이 완전하지 않습니다. AZURE_API_KEY, AZURE_ENDPOINT를 확인하세요.")
        
        return AzureOpenAIEmbeddings(
            model=model,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=os.getenv("AZURE_API_VERSION", "2024-06-01-preview"),
            **kwargs
        )


# 편의 함수들
def create_llm(provider: Optional[str] = None, **kwargs) -> BaseLanguageModel:
    """간편한 LLM 생성 함수"""
    return LLMFactory.create_llm(provider=provider, **kwargs)


def create_openai_llm(model: str = "gpt-4o", **kwargs) -> ChatOpenAI:
    """OpenAI LLM 생성 편의 함수"""
    return LLMFactory.create_llm(provider="openai", model=model, **kwargs)


def create_anthropic_llm(model: str = "claude-3-sonnet-20240229", **kwargs) -> ChatAnthropic:
    """Anthropic LLM 생성 편의 함수"""
    return LLMFactory.create_llm(provider="anthropic", model=model, **kwargs)


def create_azure_llm(model: str = "gpt-4o", **kwargs) -> AzureChatOpenAI:
    """Azure OpenAI LLM 생성 편의 함수"""
    return LLMFactory.create_llm(provider="azure", model=model, **kwargs)


def create_ollama_llm(model: str = "llama3", **kwargs) -> ChatOllama:
    """Ollama LLM 생성 편의 함수"""
    return LLMFactory.create_llm(provider="ollama", model=model, **kwargs)


# Embedding 팩토리 메서드들
def create_embedding(provider: Optional[str] = None, model: Optional[str] = None, **kwargs):
    """Embedding 인스턴스를 생성합니다."""
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    model = model or LLMFactory._get_default_embedding_model(provider)
    
    if provider == "openai":
        return LLMFactory._create_openai_embedding(model, **kwargs)
    elif provider == "azure":
        return LLMFactory._create_azure_embedding(model, **kwargs)
    elif provider in ["anthropic", "ollama"]:
        # Anthropic과 Ollama는 embedding을 지원하지 않으므로 OpenAI 사용
        return LLMFactory._create_openai_embedding(model, **kwargs)
    else:
        raise ValueError(f"지원하지 않는 embedding 제공자: {provider}")


def create_openai_embedding(model: str = "text-embedding-3-large", **kwargs):
    """OpenAI Embedding 생성 편의 함수"""
    return LLMFactory._create_openai_embedding(model, **kwargs)


def create_azure_embedding(model: str = "text-embedding-3-large", **kwargs):
    """Azure OpenAI Embedding 생성 편의 함수"""
    return LLMFactory._create_azure_embedding(model, **kwargs)
