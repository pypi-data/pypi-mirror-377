# Perigon LangChain Integration

A LangChain integration for the Perigon API, enabling seamless access to news articles and vector search capabilities within the LangChain ecosystem.

## Features

- **News Articles Search**: Semantic search through news articles using Perigon's vector search API
- **Wikipedia Search**: Semantic search through Wikipedia articles with rich metadata
- **LangChain Compatible**: Both retrievers implement LangChain's `BaseRetriever` interface
- **Async Support**: Both synchronous and asynchronous operations
- **Type Safety**: Built with the official Perigon Python SDK for robust type checking
- **Flexible Filtering**: Support for country, source, category, topic, and location-based filtering
- **Rich Metadata**: Wikipedia results include pageviews, Wikidata IDs, revision information

## Installation

```bash
pip install langchain-perigon
```

Or with Poetry:

```bash
poetry add langchain-perigon
```

## Quick Start

### News Articles Search

```python
from langchain_perigon import ArticlesRetriever, ArticlesFilter

# Initialize with API key
retriever = ArticlesRetriever(API_KEY="your_perigon_api_key")

# Or use environment variable PERIGON_API_KEY
retriever = ArticlesRetriever()

# Simple search
documents = retriever.invoke("artificial intelligence developments")

# With options
options: ArticlesFilter = {
    "size": 10,
    "showReprints": False,
    "filter": {
        "country": "us",
        "category": "tech"
    }
}
documents = retriever.invoke("machine learning breakthroughs", options=options)
```

### Wikipedia Search

```python
from langchain_perigon import WikipediaRetriever, WikipediaOptions

# Initialize Wikipedia retriever
wiki_retriever = WikipediaRetriever(API_KEY="your_perigon_api_key")

# Simple Wikipedia search
documents = wiki_retriever.invoke("quantum computing")

# With advanced options
options: WikipediaOptions = {
    "size": 5,
    "pageviewsFrom": 100,  # Only popular pages
    "filter": {
        "wikidataInstanceOfLabel": ["academic discipline"],
        "category": ["Physics", "Computer science"]
    }
}
documents = wiki_retriever.invoke("machine learning", options=options)

# Access rich metadata
for doc in documents:
    print(f"Title: {doc.metadata['title']}")
    print(f"Pageviews: {doc.metadata['pageviews']}")
    print(f"Wikidata ID: {doc.metadata['wikidataId']}")
```

### Async Usage

```python
import asyncio
from langchain_perigon import ArticlesRetriever, WikipediaRetriever, ArticlesFilter, WikipediaOptions

async def search_both():
    # News articles
    articles_retriever = ArticlesRetriever(API_KEY="your_perigon_api_key")
    articles_options: ArticlesFilter = {
        "size": 5,
        "filter": {"country": "us"}
    }
    articles = await articles_retriever.ainvoke("climate change", options=articles_options)
    
    # Wikipedia articles
    wiki_retriever = WikipediaRetriever(API_KEY="your_perigon_api_key")
    wiki_options: WikipediaOptions = {
        "size": 3,
        "pageviewsFrom": 50
    }
    wiki_docs = await wiki_retriever.ainvoke("climate change", options=wiki_options)
    
    return articles, wiki_docs

# Run async search
articles, wiki_docs = asyncio.run(search_both())
```

## Configuration

### API Key

Set your Perigon API key in one of these ways:

1. **Parameter**: `ArticlesRetriever(API_KEY="your_key")`
2. **Environment Variable**: Set `PERIGON_API_KEY` environment variable

### Filter Options

#### News Articles (`ArticlesFilter`)

```python
options: ArticlesFilter = {
    "size": 10,                    # Number of results (default: 10)
    "showReprints": False,         # Include reprints (default: False)
    "filter": {
        "country": "us",           # Country filter (string or list)
        "source": "nytimes.com",   # Source filter (string or list)  
        "category": "tech",        # Category filter (string or list)
        "topic": "ai",            # Topic filter (string or list)
        "state": "CA",            # State filter (string or list)
        "city": "San Francisco"   # City filter (string or list)
    }
}
```

#### Wikipedia Articles (`WikipediaOptions`)

```python
options: WikipediaOptions = {
    "size": 10,                           # Number of results (default: 10)
    "page": 0,                           # Page number (default: 0)
    "pageviewsFrom": 100,                # Minimum daily pageviews
    "pageviewsTo": 10000,                # Maximum daily pageviews
    "wikiRevisionFrom": "2024-01-01",    # Modified after date
    "wikiRevisionTo": "2024-12-31",      # Modified before date
    "filter": {
        "wikidataId": "Q2539",           # Specific Wikidata ID
        "wikidataInstanceOfLabel": ["academic discipline"],  # Instance type
        "category": ["Computer science"], # Wikipedia categories
        "title": "machine learning",     # Title search
        "withPageviews": True            # Only pages with view data
    }
}
```

## Integration with LangChain

Both retrievers implement LangChain's `BaseRetriever` interface and work seamlessly with other LangChain components:

### QA Chain with News Articles

```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Create news retriever
retriever = ArticlesRetriever(API_KEY="your_perigon_api_key")

# Use in a QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retriever
)

# Ask questions about recent news
result = qa_chain.run("What are the latest developments in AI?")
```

### QA Chain with Wikipedia Knowledge

```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Create Wikipedia retriever
wiki_retriever = WikipediaRetriever(API_KEY="your_perigon_api_key")

# Use in a QA chain for encyclopedic knowledge
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=wiki_retriever
)

# Ask questions about established knowledge
result = qa_chain.run("Explain the fundamentals of machine learning")
```

### Combining Both Retrievers

```python
from langchain.retrievers import EnsembleRetriever

# Create both retrievers
news_retriever = ArticlesRetriever(API_KEY="your_perigon_api_key")
wiki_retriever = WikipediaRetriever(API_KEY="your_perigon_api_key")

# Combine them for comprehensive search
ensemble_retriever = EnsembleRetriever(
    retrievers=[news_retriever, wiki_retriever],
    weights=[0.6, 0.4]  # Favor news articles slightly
)

# Use combined retriever
documents = ensemble_retriever.get_relevant_documents("artificial intelligence")
```

## Migration from v0.x

This version has been migrated to use the official Perigon Python SDK instead of raw HTTP requests. The public API remains the same, but you'll get:

- Better type safety and error handling
- Improved performance and reliability  
- Automatic retries and connection management
- Future-proof compatibility with API changes

## Development

### Running Tests

This project uses Poetry for dependency management. To run tests:

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run specific test files
poetry run pytest tests/unit_tests/imports_test.py
poetry run pytest tests/integration_tests/

# Run tests with verbose output
poetry run pytest -v
```

### Running Examples

Examples require a valid Perigon API key:

```bash
# Set your API key
export PERIGON_API_KEY=your_actual_api_key

# Run examples with poetry
poetry run python examples/simple_test.py
poetry run python examples/wikipedia_example.py
```

### Performance Optimizations

This version includes several performance improvements:

- **Optimized metadata transformation**: Reduced reflection-based attribute access
- **Configurable timeouts**: Set custom timeout values for API calls
- **Error handling**: Graceful fallbacks for transformation errors
- **Efficient processing**: Streamlined data extraction pipelines

You can configure timeout settings:

```python
# Set custom timeout (default: 30 seconds)
retriever = ArticlesRetriever(API_KEY="your_key", timeout=60)
wiki_retriever = WikipediaRetriever(API_KEY="your_key", timeout=45)
```

## Requirements

- Python 3.11+
- LangChain Core
- Perigon Python SDK

## License

MIT