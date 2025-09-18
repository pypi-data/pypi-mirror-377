from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="process-gpt-llm-factory",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="통합 LLM 팩토리 라이브러리 - 다양한 LLM 제공자를 통합된 인터페이스로 사용",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-factory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.3.0",
        "langchain-openai>=0.3.0",
        "langchain-anthropic>=0.3.0",
        "langchain-ollama>=0.3.0",
        "langchain-core>=0.3.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="llm, openai, azure, anthropic, ollama, langchain, factory, ai, machine learning",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/llm-factory/issues",
        "Source": "https://github.com/yourusername/llm-factory",
        "Documentation": "https://github.com/yourusername/llm-factory#readme",
    },
)
