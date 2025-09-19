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
from perigon.models.wikipedia_search_params import WikipediaSearchParams

from langchain_perigon.types import WikipediaOptions


class WikipediaRetriever(BaseRetriever):
    """Retrieves Wikipedia articles from Perigon Vector Search"""

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
        options: Optional[WikipediaOptions] = None,
        **kwargs
    ) -> List[Document]:
        """Invoke the retriever with optional WikipediaOptions."""
        if options is not None:
            kwargs["options"] = options
        return super().invoke(input, config, **kwargs)

    async def ainvoke(
        self, 
        input: str, 
        config: Optional[RunnableConfig] = None, 
        *,
        options: Optional[WikipediaOptions] = None,
        **kwargs
    ) -> List[Document]:
        """Async invoke the retriever with optional WikipediaOptions."""
        if options is not None:
            kwargs["options"] = options
        return await super().ainvoke(input, config, **kwargs)

    def transform_wikipedia_to_documents(self, results: List) -> List[Document]:
        """Transform Wikipedia search results to LangChain documents with optimized metadata extraction."""
        docs = []

        for result in results:
            try:
                # Fast path: direct attribute access
                data = result.data
                score = result.score
                content = getattr(data, "content", "")

                # Build core metadata efficiently
                metadata = {
                    "score": score,
                    "source": "wikipedia",
                    "title": getattr(data, "wiki_title", None),
                    "pageviews": getattr(data, "pageviews", None),
                    "wikidataId": getattr(data, "wikidata_id", None),
                    "wikiPageId": getattr(data, "wiki_page_id", None),
                    "wikiRevisionTs": getattr(data, "wiki_revision_ts", None),
                    "wikidataInstanceOf": getattr(data, "wikidata_instance_of", None),
                    "pageId": getattr(data, "page_id", None),
                    "sectionId": getattr(data, "section_id", None),
                    "wikiCode": getattr(data, "wiki_code", None),
                    "wikiNamespace": getattr(data, "wiki_namespace", None),
                    "redirectTitles": getattr(data, "redirect_titles", None),
                    "styleLevel": getattr(data, "style_level", None),
                }

                # Keep all metadata fields for test compatibility
                # Tests expect these fields to exist even if None

                # Create document
                docs.append(Document(page_content=content, metadata=metadata))

            except Exception as e:
                # Fallback for any transformation errors
                docs.append(Document(
                    page_content=str(result), 
                    metadata={"error": f"Transformation failed: {str(e)}", "source": "wikipedia"}
                ))

        return docs

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs,
    ) -> List[Document]:
        """Sync implementation for Wikipedia retriever."""
        # Support k parameter from kwargs or use instance default
        k = kwargs.get("k", self.k)
        
        # Extract options from kwargs if provided
        options = kwargs.get("options", {})
        
        # Convert options to SDK parameters
        search_params = WikipediaSearchParams(
            prompt=query,
            size=options.get("size", k),
            page=options.get("page", 0),
            pageviews_from=options.get("pageviewsFrom"),
            pageviews_to=options.get("pageviewsTo"),
            wiki_revision_from=options.get("wikiRevisionFrom"),
            wiki_revision_to=options.get("wikiRevisionTo"),
            **self._convert_wikipedia_filter_options(options.get("filter", {}))
        )

        # Use SDK to perform Wikipedia vector search
        response = self._client.vector_search_wikipedia(
            wikipedia_search_params=search_params
        )

        # Extract results from response
        results = response.results if hasattr(response, "results") else []

        return self.transform_wikipedia_to_documents(results)

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
        **kwargs,
    ) -> List[Document]:
        """Async implementation for Wikipedia retriever."""
        # Support k parameter from kwargs or use instance default
        k = kwargs.get("k", self.k)
        
        # Extract options from kwargs if provided
        options = kwargs.get("options", {})
        
        # Convert options to SDK parameters
        search_params = WikipediaSearchParams(
            prompt=query,
            size=options.get("size", k),
            page=options.get("page", 0),
            pageviews_from=options.get("pageviewsFrom"),
            pageviews_to=options.get("pageviewsTo"),
            wiki_revision_from=options.get("wikiRevisionFrom"),
            wiki_revision_to=options.get("wikiRevisionTo"),
            **self._convert_wikipedia_filter_options(options.get("filter", {}))
        )

        # Use SDK async method to perform Wikipedia vector search
        response = await self._client.vector_search_wikipedia_async(
            wikipedia_search_params=search_params
        )

        # Extract results from response
        results = response.results if hasattr(response, "results") else []

        return self.transform_wikipedia_to_documents(results)

    def _convert_wikipedia_filter_options(self, filter_options: dict) -> dict:
        """Convert WikipediaFilter options to SDK-compatible parameters."""
        converted = {}

        # Map Wikipedia filter options to SDK parameters
        if "wikidataId" in filter_options:
            converted["wikidata_id"] = (
                filter_options["wikidataId"]
                if isinstance(filter_options["wikidataId"], list)
                else [filter_options["wikidataId"]]
            )
        if "wikidataInstanceOfId" in filter_options:
            converted["wikidata_instance_of_id"] = (
                filter_options["wikidataInstanceOfId"]
                if isinstance(filter_options["wikidataInstanceOfId"], list)
                else [filter_options["wikidataInstanceOfId"]]
            )
        if "wikidataInstanceOfLabel" in filter_options:
            converted["wikidata_instance_of_label"] = (
                filter_options["wikidataInstanceOfLabel"]
                if isinstance(filter_options["wikidataInstanceOfLabel"], list)
                else [filter_options["wikidataInstanceOfLabel"]]
            )
        if "wikiCode" in filter_options:
            converted["wiki_code"] = (
                filter_options["wikiCode"]
                if isinstance(filter_options["wikiCode"], list)
                else [filter_options["wikiCode"]]
            )
        if "category" in filter_options:
            converted["category"] = (
                filter_options["category"]
                if isinstance(filter_options["category"], list)
                else [filter_options["category"]]
            )
        if "title" in filter_options:
            converted["title"] = filter_options["title"]
        if "summary" in filter_options:
            converted["summary"] = filter_options["summary"]
        if "text" in filter_options:
            converted["text"] = filter_options["text"]
        if "reference" in filter_options:
            converted["reference"] = filter_options["reference"]
        if "withPageviews" in filter_options:
            converted["with_pageviews"] = filter_options["withPageviews"]

        return converted
