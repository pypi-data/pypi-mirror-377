# LLM Factory

[![PyPI version](https://badge.fury.io/py/llm-factory.svg)](https://badge.fury.io/py/llm-factory)
[![Python Support](https://img.shields.io/pypi/pyversions/llm-factory.svg)](https://pypi.org/project/llm-factory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

통합 LLM 팩토리 라이브러리 - 다양한 LLM 제공자를 통합된 인터페이스로 사용할 수 있게 해주는 Python 라이브러리입니다.

## 주요 기능

- **다중 LLM 제공자 지원**: OpenAI, Azure OpenAI, Anthropic, Ollama

## 설치

requirements.txt에 추가:

```txt
process-gpt-llm-factory==1.0.0
```

### 직접 설치
```bash
pip install process-gpt-llm-factory
```

## 빠른 시작

### 1. 환경변수 설정

`.env` 파일에 다음 환경변수들을 설정하세요:

```bash
# LLM Provider 설정 (설정하지 않는 경우 openai 기본값 사용)
LLM_PROVIDER=openai  # openai, azure, anthropic, ollama 중 선택

# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# 아래 설정은 openai 외 사용시에만 필요
# Azure OpenAI 설정
AZURE_API_KEY=your_azure_api_key_here
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT=your_deployment_name
AZURE_MODEL=gpt-4o
AZURE_API_VERSION=2024-06-01-preview

# Anthropic 설정
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama 설정
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. 기본 사용법

```python
from llm_factory import create_llm, create_embedding

# 환경변수에 설정된 제공자와 모델 사용
llm = create_llm()

# 특정 제공자 지정
llm = create_llm(provider="openai")

# 특정 모델과 옵션 지정
llm = create_llm(
    model="gpt-4o",
    temperature=0.7,
    streaming=True
)

## API 참조

### LLM 생성 함수

```python
from llm_factory import (
    create_llm,
    create_openai_llm,
    create_azure_llm,
    create_anthropic_llm,
    create_ollama_llm
)

# 기본 LLM 생성 
llm = create_llm()

# 특정 제공자 LLM 생성 
openai_llm = create_openai_llm(model="gpt-4o", temperature=0.5)
azure_llm = create_azure_llm(model="gpt-4o")
anthropic_llm = create_anthropic_llm(model="claude-3-sonnet-20240229")
ollama_llm = create_ollama_llm(model="llama3")
```

### Embedding 생성 함수

```python
from llm_factory import (
    create_embedding,
    create_openai_embedding,
    create_azure_embedding
)

# 기본 Embedding 생성 (환경변수 기반)
embedding = create_embedding()

# 특정 제공자 Embedding 생성
openai_embedding = create_openai_embedding(model="text-embedding-3-large")
azure_embedding = create_azure_embedding(model="text-embedding-3-large")
```

## 마이그레이션 가이드

기존 코드에서 직접 LLM을 생성하던 방식을 LLM Factory로 변경하는 방법:

### Before (기존 방식)
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0)
```

### After (LLM Factory 사용)
```python
from llm_factory import create_llm

model = create_llm(temperature=0)
```

