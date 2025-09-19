from typing import List, Optional, Union

from langchain_core.callbacks import (
    CallbackManagerForRetrieverRun,
    AsyncCallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig
from pydantic import Field

import os
from perigon import V1Api, ApiClient
from perigon.models.article_search_params import ArticleSearchParams

from langchain_perigon.types import ArticlesFilter


class ArticlesRetriever(BaseRetriever):
    """Retrieves articles from Perigon Vector Search"""

    API_KEY: Optional[str] = Field(default=None)
    k: int = Field(default=10)
    timeout: int = Field(default=60)

    def __init__(self, API_KEY: str = None, k: int = 10, timeout: int = 60, **kwargs):
        # Get API key from parameter or environment
        api_key = API_KEY or os.getenv("PERIGON_API_KEY")
        if not api_key:
            raise ValueError(
                "PERIGON_API_KEY must be provided either as parameter or environment variable"
            )

        super().__init__(API_KEY=api_key, k=k, timeout=timeout, **kwargs)

        # Set the client directly as an object attribute (not a Pydantic field)
        # Pass timeout directly to ApiClient constructor
        api_client = ApiClient(api_key=self.API_KEY, timeout=timeout)
        object.__setattr__(self, "_client", V1Api(api_client))

    def invoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        *,
        options: Optional[ArticlesFilter] = None,
        **kwargs,
    ) -> List[Document]:
        """Invoke the retriever with optional ArticlesFilter."""
        if options is not None:
            kwargs["options"] = options
        return super().invoke(input, config, **kwargs)

    async def ainvoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        *,
        options: Optional[ArticlesFilter] = None,
        **kwargs,
    ) -> List[Document]:
        """Async invoke the retriever with optional ArticlesFilter."""
        if options is not None:
            kwargs["options"] = options
        return await super().ainvoke(input, config, **kwargs)

    def transform_articles_to_documents(self, articles: List) -> List[Document]:
        """Transform articles with optimized metadata extraction from Perigon API response."""
        docs_transformed = []

        for article in articles:
            try:
                # Fast path: direct attribute access with fallback
                article_data = article.data if hasattr(article, "data") else None
                if not article_data:
                    # Fallback for different response structures
                    docs_transformed.append(
                        Document(page_content=str(article), metadata={})
                    )
                    continue

                # Extract content efficiently
                content = (
                    getattr(article_data, "summary", None)
                    or getattr(article_data, "title", "")
                    or ""
                )

                # Build core metadata with direct access
                metadata = self._extract_core_metadata(article_data)

                # Add relevance score if available
                if hasattr(article, "score"):
                    metadata["relevanceScore"] = article.score

                # Extract source information efficiently
                self._extract_source_metadata(article_data, metadata)

                # Extract classification data efficiently
                self._extract_classification_metadata(article_data, metadata)

                # Create Document with content and metadata
                docs_transformed.append(
                    Document(page_content=content, metadata=metadata)
                )

            except Exception as e:
                # Fallback for any transformation errors
                docs_transformed.append(
                    Document(
                        page_content=str(article),
                        metadata={"error": f"Transformation failed: {str(e)}"},
                    )
                )

        return docs_transformed

    def _extract_core_metadata(self, article_data) -> dict:
        """Extract core article metadata efficiently."""
        return {
            "articleId": getattr(article_data, "article_id", None),
            "clusterId": getattr(article_data, "cluster_id", None),
            "url": getattr(article_data, "url", None),
            "title": getattr(article_data, "title", None),
            "authorsByLine": getattr(article_data, "authors_by_line", None),
            "pubDate": getattr(article_data, "pub_date", None),
            "addDate": getattr(article_data, "add_date", None),
            "language": getattr(article_data, "language", None),
            "country": getattr(article_data, "country", None),
            "imageUrl": getattr(article_data, "image_url", None),
            "reprint": getattr(article_data, "reprint", False),
            "reprintGroupId": getattr(article_data, "reprint_group_id", None),
        }

    def _extract_source_metadata(self, article_data, metadata: dict) -> None:
        """Extract source metadata efficiently."""
        source = getattr(article_data, "source", None)
        if not source:
            return

        metadata["sourceDomain"] = getattr(source, "domain", None)

        location = getattr(source, "location", None)
        if location:
            metadata.update(
                {
                    "sourceCountry": getattr(location, "country", None),
                    "sourceState": getattr(location, "state", None),
                    "sourceCity": getattr(location, "city", None),
                    "sourceCounty": getattr(location, "county", None),
                }
            )

            coords = getattr(location, "coordinates", None)
            if coords:
                metadata.update(
                    {
                        "sourceLat": getattr(coords, "lat", None),
                        "sourceLon": getattr(coords, "lon", None),
                    }
                )

    def _extract_classification_metadata(self, article_data, metadata: dict) -> None:
        """Extract classification metadata efficiently."""
        # Extract topics
        topics = getattr(article_data, "topics", None)
        if topics:
            metadata["topics"] = [
                getattr(topic, "name", "") for topic in topics if hasattr(topic, "name")
            ]

        # Extract categories
        categories = getattr(article_data, "categories", None)
        if categories:
            metadata["categories"] = [
                getattr(cat, "name", "") for cat in categories if hasattr(cat, "name")
            ]

        # Extract labels (most commonly used)
        labels = getattr(article_data, "labels", None)
        if labels:
            metadata["labels"] = [
                getattr(label, "name", "") for label in labels if hasattr(label, "name")
            ]

        # Skip heavy processing for entities, companies, people, locations unless needed
        # These can be added back if specifically required for the use case

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs,
    ) -> List[Document]:
        """Sync implementations for retriever."""
        # Support k parameter from kwargs or use instance default
        k = kwargs.get("k", self.k)

        # Extract options from kwargs if provided
        options = kwargs.get("options", {})

        # Convert options to SDK parameters
        search_params = ArticleSearchParams(
            prompt=query,
            size=options.get("size", k),
            show_reprints=options.get("showReprints", False),
            **self._convert_filter_options(options.get("filter", {})),
        )

        # Use SDK to perform vector search
        response = self._client.vector_search_articles(
            article_search_params=search_params
        )

        # Extract articles from response
        articles = response.results if hasattr(response, "results") else []

        return self.transform_articles_to_documents(articles)

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
        **kwargs,
    ) -> List[Document]:
        """Async implementation for retriever."""
        # Support k parameter from kwargs or use instance default
        k = kwargs.get("k", self.k)

        # Extract options from kwargs if provided
        options = kwargs.get("options", {})

        # Convert options to SDK parameters
        search_params = ArticleSearchParams(
            prompt=query,
            size=options.get("size", k),
            show_reprints=options.get("showReprints", False),
            **self._convert_filter_options(options.get("filter", {})),
        )

        # Use SDK async method to perform vector search
        response = await self._client.vector_search_articles_async(
            article_search_params=search_params
        )

        # Extract articles from response
        articles = response.results if hasattr(response, "results") else []

        return self.transform_articles_to_documents(articles)

    def _convert_filter_options(self, filter_options: dict) -> dict:
        """Convert ArticlesFilter options to SDK-compatible parameters."""
        converted = {}

        # Map common filter options to SDK parameters
        if "country" in filter_options:
            converted["countries"] = (
                filter_options["country"]
                if isinstance(filter_options["country"], list)
                else [filter_options["country"]]
            )
        if "source" in filter_options:
            converted["sources"] = (
                filter_options["source"]
                if isinstance(filter_options["source"], list)
                else [filter_options["source"]]
            )
        if "category" in filter_options:
            converted["categories"] = (
                filter_options["category"]
                if isinstance(filter_options["category"], list)
                else [filter_options["category"]]
            )
        if "topic" in filter_options:
            converted["topics"] = (
                filter_options["topic"]
                if isinstance(filter_options["topic"], list)
                else [filter_options["topic"]]
            )
        if "state" in filter_options:
            converted["states"] = (
                filter_options["state"]
                if isinstance(filter_options["state"], list)
                else [filter_options["state"]]
            )
        if "city" in filter_options:
            converted["cities"] = (
                filter_options["city"]
                if isinstance(filter_options["city"], list)
                else [filter_options["city"]]
            )

        return converted
