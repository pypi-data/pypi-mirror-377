import argparse
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from mcp.server.fastmcp import Context, FastMCP
from pymilvus import (
    AnnSearchRequest,
    DataType,
    MilvusClient,
    RRFRanker,
)


class MilvusConnector:
    def __init__(self, uri: str, token: Optional[str] = None, db_name: Optional[str] = "default"):
        self.uri = uri
        self.token = token if token is not None else ""
        self.db_name = db_name if db_name is not None else "default"
        self.client = MilvusClient(uri=uri, token=self.token, db_name=self.db_name)

    @classmethod
    def from_env(cls) -> "MilvusConnector":
        """
        Create a MilvusConnector instance from environment variables.

        Environment variables:
        - MILVUS_URI: Milvus server URI (required)
        - MILVUS_TOKEN: Authentication token (optional)
        - MILVUS_DB: Database name (defaults to "default")
        """
        uri = os.environ.get("MILVUS_URI")
        if not uri:
            raise ValueError("MILVUS_URI environment variable must be set")

        token = os.environ.get("MILVUS_TOKEN")
        db_name = os.environ.get("MILVUS_DB", "default")

        return cls(uri=uri, token=token, db_name=db_name)

    async def list_collections(self) -> list[str]:
        """List all collections in the database."""
        try:
            return self.client.list_collections()
        except Exception as e:
            raise ValueError(f"Failed to list collections: {str(e)}") from e

    async def get_collection_info(self, collection_name: str) -> dict:
        """Get detailed information about a collection."""
        try:
            return self.client.describe_collection(collection_name)
        except Exception as e:
            raise ValueError(f"Failed to get collection info: {str(e)}") from e

    async def search_collection(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 5,
        output_fields: Optional[list[str]] = None,
        drop_ratio: float = 0.2,
    ) -> list[dict]:
        """
        Perform full text search on a collection.

        Args:
            collection_name: Name of collection to search
            query_text: Text to search for
            limit: Maximum number of results
            output_fields: Fields to return in results
            drop_ratio: Proportion of low-frequency terms to ignore (0.0-1.0)
        """
        try:
            search_params = {"params": {"drop_ratio_search": drop_ratio}}

            results = self.client.search(
                collection_name=collection_name,
                data=[query_text],
                anns_field="sparse",
                limit=limit,
                output_fields=output_fields,
                search_params=search_params,
            )
            return results
        except Exception as e:
            raise ValueError(f"Search failed: {str(e)}") from e

    async def query_collection(
        self,
        collection_name: str,
        filter_expr: str,
        output_fields: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Query collection using filter expressions."""
        try:
            return self.client.query(
                collection_name=collection_name,
                filter=filter_expr,
                output_fields=output_fields,
                limit=limit,
            )
        except Exception as e:
            raise ValueError(f"Query failed: {str(e)}") from e

    async def vector_search(
        self,
        collection_name: str,
        vector: list[float],
        vector_field: str,
        limit: int = 5,
        output_fields: Optional[list[str]] = None,
        metric_type: str = "COSINE",
        filter_expr: Optional[str] = None,
    ) -> list[dict]:
        """
        Perform vector similarity search on a collection.

        Args:
            collection_name: Name of collection to search
            vector: Query vector
            vector_field: Field containing vectors to search
            limit: Maximum number of results
            output_fields: Fields to return in results
            metric_type: Distance metric (COSINE, L2, IP)
            filter_expr: Optional filter expression
        """
        try:
            search_params = {"metric_type": metric_type, "params": {"nprobe": 10}}

            results = self.client.search(
                collection_name=collection_name,
                data=[vector],
                anns_field=vector_field,
                search_params=search_params,
                limit=limit,
                output_fields=output_fields,
                filter=filter_expr if filter_expr is not None else "",
            )
            # Flatten results if nested
            def flatten(lst):
                flat = []
                for item in lst:
                    if isinstance(item, list):
                        flat.extend(flatten(item))
                    else:
                        flat.append(item)
                return flat
            if isinstance(results, list):
                return flatten(results)
            return []
        except Exception as e:
            raise ValueError(f"Vector search failed: {str(e)}") from e

    async def hybrid_search(
        self,
        collection_name: str,
        query_text: str,
        text_field: str,
        vector: list[float],
        vector_field: str,
        limit: int,
        output_fields: Optional[list[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> list[dict]:
        """
        Perform hybrid search combining BM25 text search and vector search with RRF ranking.

        Args:
            collection_name: Name of collection to search
            query_text: Text query for BM25 search
            text_field: Field name for text search
            vector: Query vector for dense vector search
            vector_field: Field name for vector search
            limit: Maximum number of results
            output_fields: Fields to return in results
            filter_expr: Optional filter expression
        """
        try:
            sparse_params = {"params": {"nprobe": 10}}
            dense_params = {"params": {"drop_ratio_build": 0.2}}
            # BM25 search request
            sparse_request = AnnSearchRequest(
                data=[query_text],
                anns_field=text_field,
                param=sparse_params,
                limit=limit,
            )
            # dense vector search request
            dense_request = AnnSearchRequest(
                data=[vector],
                anns_field=vector_field,
                param=dense_params,
                limit=limit,
            )
            # hybrid search
            results = self.client.hybrid_search(
                collection_name=collection_name,
                reqs=[sparse_request, dense_request],
                ranker=RRFRanker(60),
                limit=limit,
                output_fields=output_fields,
                filter=filter_expr if filter_expr is not None else "",
            )
            # Flatten results if nested
            if results and isinstance(results[0], list):
                return [item for sublist in results for item in sublist]
            return results if results else []

        except Exception as e:
            raise ValueError(f"Hybrid search failed: {str(e)}") from e

    async def create_collection(
        self,
        collection_name: str,
        schema: dict[str, Any],
        index_params: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Create a new collection with the specified schema.

        Args:
            collection_name: Name for the new collection
            schema: Collection schema definition
            index_params: Optional index parameters
        """
        try:
            # Check if collection already exists
            if collection_name in self.client.list_collections():
                raise ValueError(f"Collection '{collection_name}' already exists")

            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                dimension=schema.get("dimension", 128),
                primary_field=schema.get("primary_field", "id"),
                id_type=schema.get("id_type", DataType.INT64),
                vector_field=schema.get("vector_field", "vector"),
                metric_type=schema.get("metric_type", "COSINE"),
                auto_id=schema.get("auto_id", False),
                enable_dynamic_field=schema.get("enable_dynamic_field", True),
                other_fields=schema.get("other_fields", []),
            )

            # Create index if params provided
            if index_params:
                self.client.create_index(
                    collection_name=collection_name,
                    field_name=schema.get("vector_field", "vector"),
                    index_params=index_params,
                )

            return True
        except Exception as e:
            raise ValueError(f"Failed to create collection: {str(e)}") from e

    async def insert_data(self, collection_name: str, data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Insert data into a collection.

        Args:
            collection_name: Name of collection
            data: List of dictionaries, each representing a record
        """
        try:
            result = self.client.insert(collection_name=collection_name, data=data)
            return result
        except Exception as e:
            raise ValueError(f"Insert failed: {str(e)}") from e

    async def delete_entities(self, collection_name: str, filter_expr: str) -> dict[str, Any]:
        """
        Delete entities from a collection based on filter expression.

        Args:
            collection_name: Name of collection
            filter_expr: Filter expression to select entities to delete
        """
        try:
            result = self.client.delete(collection_name=collection_name, expr=filter_expr)
            return result
        except Exception as e:
            raise ValueError(f"Delete failed: {str(e)}") from e

    async def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        """
        Get statistics about a collection.

        Args:
            collection_name: Name of collection
        """
        try:
            return self.client.get_collection_stats(collection_name)
        except Exception as e:
            raise ValueError(f"Failed to get collection stats: {str(e)}") from e

    async def multi_vector_search(
        self,
        collection_name: str,
        vectors: list[list[float]],
        vector_field: str,
        limit: int = 5,
        output_fields: Optional[list[str]] = None,
        metric_type: str = "COSINE",
        filter_expr: Optional[str] = None,
        search_params: Optional[dict[str, Any]] = None,
    ) -> list[dict]:
        """
        Perform vector similarity search with multiple query vectors.

        Args:
            collection_name: Name of collection to search
            vectors: List of query vectors
            vector_field: Field containing vectors to search
            limit: Maximum number of results per query
            output_fields: Fields to return in results
            metric_type: Distance metric (COSINE, L2, IP)
            filter_expr: Optional filter expression
            search_params: Additional search parameters
        """
        try:
            if search_params is None:
                search_params = {"metric_type": metric_type, "params": {"nprobe": 10}}

            results = self.client.search(
                collection_name=collection_name,
                data=vectors,
                anns_field=vector_field,
                search_params=search_params,
                limit=limit,
                output_fields=output_fields,
                filter=filter_expr if filter_expr is not None else "",
            )
            # Flatten results if nested
            if results and isinstance(results[0], list):
                return [item for sublist in results for item in sublist]
            return results if results else []
        except Exception as e:
            raise ValueError(f"Multi-vector search failed: {str(e)}") from e

    async def create_index(
        self,
        collection_name: str,
        field_name: str,
        index_type: str = "IVF_FLAT",
        metric_type: str = "COSINE",
        params: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Create an index on a vector field.

        Args:
            collection_name: Name of collection
            field_name: Field to index
            index_type: Type of index (IVF_FLAT, HNSW, etc.)
            metric_type: Distance metric (COSINE, L2, IP)
            params: Additional index parameters
        """
        try:
            if params is None:
                params = {"nlist": 1024}

            index_params = {
                "index_type": index_type,
                "metric_type": metric_type,
                "params": params,
            }

            self.client.create_index(
                collection_name=collection_name,
                field_name=field_name,
                index_params=index_params,
            )
            return True
        except Exception as e:
            raise ValueError(f"Failed to create index: {str(e)}") from e

    async def bulk_insert(
        self, collection_name: str, data: dict[str, list[Any]], batch_size: int = 1000
    ) -> list[dict[str, Any]]:
        """
        Insert data in batches for better performance.

        Args:
            collection_name: Name of collection
            data: Dictionary mapping field names to lists of values
            batch_size: Number of records per batch
        """
        try:
            results = []
            field_names = list(data.keys())
            total_records = len(data[field_names[0]])

            for i in range(0, total_records, batch_size):
                batch_data = {field: data[field][i : i + batch_size] for field in field_names}

                result = self.client.insert(collection_name=collection_name, data=batch_data)
                results.append(result)

            return results
        except Exception as e:
            raise ValueError(f"Bulk insert failed: {str(e)}") from e

    async def load_collection(self, collection_name: str, replica_number: int = 1) -> bool:
        """
        Load a collection into memory for search and query.

        Args:
            collection_name: Name of collection to load
            replica_number: Number of replicas
        """
        try:
            self.client.load_collection(
                collection_name=collection_name, replica_number=replica_number
            )
            return True
        except Exception as e:
            raise ValueError(f"Failed to load collection: {str(e)}") from e

    async def release_collection(self, collection_name: str) -> bool:
        """
        Release a collection from memory.

        Args:
            collection_name: Name of collection to release
        """
        try:
            self.client.release_collection(collection_name=collection_name)
            return True
        except Exception as e:
            raise ValueError(f"Failed to release collection: {str(e)}") from e

    # REMOVED: get_query_segment_info (unknown attribute on MilvusClient)

    async def upsert_data(self, collection_name: str, data: dict[str, list[Any]]) -> dict[str, Any]:
        """
        Upsert data into a collection (insert or update if exists).

        Args:
            collection_name: Name of collection
            data: Dictionary mapping field names to lists of values
        """
        try:
            result = self.client.upsert(collection_name=collection_name, data=data)
            return result
        except Exception as e:
            raise ValueError(f"Upsert failed: {str(e)}") from e

    async def get_index_info(
        self, collection_name: str, field_name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get information about indexes in a collection.

        Args:
            collection_name: Name of collection
            field_name: Optional specific field to get index info for
        """
        try:
            return self.client.describe_index(
                collection_name=collection_name, index_name=field_name if field_name is not None else ""
            )
        except Exception as e:
            raise ValueError(f"Failed to get index info: {str(e)}") from e

    async def get_collection_loading_progress(self, collection_name: str) -> dict[str, Any]:
        """
        Get the loading progress of a collection.

        Args:
            collection_name: Name of collection
        """
        try:
            return self.client.get_load_state(collection_name)
        except Exception as e:
            raise ValueError(f"Failed to get loading progress: {str(e)}") from e

    async def list_databases(self) -> list[str]:
        """List all databases in the Milvus instance."""
        try:
            return self.client.list_databases()
        except Exception as e:
            raise ValueError(f"Failed to list databases: {str(e)}") from e

    async def use_database(self, db_name: str) -> bool:
        """Switch to a different database.

        Args:
            db_name: Name of the database to use
        """
        try:
            # Create a new client with the specified database
            self.client = MilvusClient(uri=self.uri, token=self.token if self.token is not None else "", db_name=db_name if db_name is not None else "default")
            return True
        except Exception as e:
            raise ValueError(f"Failed to switch database: {str(e)}") from e


class MilvusContext:
    def __init__(self, connector: MilvusConnector):
        self.connector = connector


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[MilvusContext]:
    """Manage application lifecycle for Milvus connector."""
    try:
        connector = MilvusConnector.from_env()
        yield MilvusContext(connector)
    finally:
        pass


mcp = FastMCP(name="Milvus", lifespan=server_lifespan)


@mcp.tool()
async def milvus_text_search(
    ctx: Context,
    collection_name: str,
    query_text: str,
    limit: int = 5,
    output_fields: Optional[list[str]] = None,
    drop_ratio: float = 0.2,
) -> dict:
    """
    Search for documents using full text search in a Milvus collection.

    Args:
        collection_name: Name of the collection to search
        query_text: Text to search for
        limit: Maximum number of results to return
        output_fields: Fields to include in results
        drop_ratio: Proportion of low-frequency terms to ignore (0.0-1.0)
    """
    connector = ctx.request_context.lifespan_context.connector
    results = await connector.search_collection(
        collection_name=collection_name,
        query_text=query_text,
        limit=limit,
        output_fields=output_fields,
        drop_ratio=drop_ratio,
    )

    return {
        "collection_name": collection_name,
        "query_text": query_text,
        "limit": limit,
        "output_fields": output_fields,
        "drop_ratio": drop_ratio,
        "results": results,
    }


@mcp.tool()
async def milvus_list_collections(ctx: Context) -> dict:
    """List all collections in the database."""
    connector = ctx.request_context.lifespan_context.connector
    collections = await connector.list_collections()
    return {
        "collections": collections
    }


@mcp.tool()
async def milvus_query(
    ctx: Context,
    collection_name: str,
    filter_expr: str,
    output_fields: Optional[list[str]] = None,
    limit: int = 10,
) -> dict:
    """
    Query collection using filter expressions.

    Args:
        collection_name: Name of the collection to query
        filter_expr: Filter expression (e.g. 'age > 20')
        output_fields: Fields to include in results
        limit: Maximum number of results
    """
    connector = ctx.request_context.lifespan_context.connector
    results = await connector.query_collection(
        collection_name=collection_name,
        filter_expr=filter_expr,
        output_fields=output_fields,
        limit=limit,
    )

    return {
        "collection_name": collection_name,
        "filter_expr": filter_expr,
        "output_fields": output_fields,
        "limit": limit,
        "results": results,
    }


@mcp.tool()
async def milvus_vector_search(
    ctx: Context,
    collection_name: str,
    vector: list[float],
    vector_field: str = "vector",
    limit: int = 5,
    output_fields: Optional[list[str]] = None,
    metric_type: str = "COSINE",
    filter_expr: Optional[str] = None,
) -> dict:
    """
    Perform vector similarity search on a collection.

    Args:
        collection_name: Name of the collection to search
        vector: Query vector
        vector_field: Field containing vectors to search
        limit: Maximum number of results
        output_fields: Fields to include in results
        metric_type: Distance metric (COSINE, L2, IP)
        filter_expr: Optional filter expression
    """
    connector = ctx.request_context.lifespan_context.connector
    results = await connector.vector_search(
        collection_name=collection_name,
        vector=vector,
        vector_field=vector_field,
        limit=limit,
        output_fields=output_fields,
        metric_type=metric_type,
        filter_expr=filter_expr,
    )

    return {
        "collection_name": collection_name,
        "vector": vector,
        "vector_field": vector_field,
        "limit": limit,
        "output_fields": output_fields,
        "metric_type": metric_type,
        "filter_expr": filter_expr,
        "results": results,
    }


@mcp.tool()
async def milvus_hybrid_search(
    ctx: Context,
    collection_name: str,
    query_text: str,
    text_field: str,
    vector: list[float],
    vector_field: str,
    limit: int = 5,
    output_fields: Optional[list[str]] = None,
    filter_expr: Optional[str] = None,
) -> dict:
    """
    Perform hybrid search combining text and vector search.

    Args:
        collection_name: Name of collection to search
        query_text: Text query for BM25 search
        text_field: Field name for text search
        vector: Query vector for dense vector search
        vector_field: Field name for vector search
        limit: Maximum number of results
        output_fields: Fields to return in results
        filter_expr: Optional filter expression
    """
    connector = ctx.request_context.lifespan_context.connector

    results = await connector.hybrid_search(
        collection_name=collection_name,
        query_text=query_text,
        text_field=text_field,
        vector=vector,
        vector_field=vector_field,
        limit=limit,
        output_fields=output_fields,
        filter_expr=filter_expr,
    )

    return {
        "collection_name": collection_name,
        "query_text": query_text,
        "text_field": text_field,
        "vector": vector,
        "vector_field": vector_field,
        "limit": limit,
        "output_fields": output_fields,
        "filter_expr": filter_expr,
        "results": results,
    }


@mcp.tool()
async def milvus_create_collection(
    ctx: Context,
    collection_name: str,
    collection_schema: dict[str, Any],
    index_params: Optional[dict[str, Any]] = None,
) -> dict:
    """
    Create a new collection with specified schema.

    Args:
        collection_name: Name for the new collection
        collection_schema: Collection schema definition
        index_params: Optional index parameters
    """
    connector = ctx.request_context.lifespan_context.connector
    success = await connector.create_collection(
        collection_name=collection_name,
        schema=collection_schema,
        index_params=index_params,
    )

    return {
        "collection_name": collection_name,
        "success": success,
        "message": f"Collection '{collection_name}' created successfully" if success else f"Failed to create collection '{collection_name}'"
    }


@mcp.tool()
async def milvus_insert_data(
    ctx: Context, collection_name: str, data: list[dict[str, Any]]
) -> dict:
    """
    Insert data into a collection.

    Args:
        collection_name: Name of collection
        data: List of dictionaries, each representing a record
    """
    connector = ctx.request_context.lifespan_context.connector
    result = await connector.insert_data(collection_name=collection_name, data=data)

    return {
        "collection_name": collection_name,
        "result": result,
        "message": f"Data inserted into collection '{collection_name}'"
    }


@mcp.tool()
async def milvus_delete_entities(
    ctx: Context, collection_name: str, filter_expr: str
) -> dict:
    """
    Delete entities from a collection based on filter expression.

    Args:
        collection_name: Name of collection
        filter_expr: Filter expression to select entities to delete
    """
    connector = ctx.request_context.lifespan_context.connector
    result = await connector.delete_entities(
        collection_name=collection_name, filter_expr=filter_expr
    )

    return {
        "collection_name": collection_name,
        "filter_expr": filter_expr,
        "result": result,
        "message": f"Entities deleted from collection '{collection_name}'"
    }


@mcp.tool()
async def milvus_load_collection(
    ctx: Context, collection_name: str, replica_number: int = 1
) -> dict:
    """
    Load a collection into memory for search and query.

    Args:
        collection_name: Name of collection to load
        replica_number: Number of replicas
    """
    connector = ctx.request_context.lifespan_context.connector
    success = await connector.load_collection(
        collection_name=collection_name, replica_number=replica_number
    )

    return {
        "collection_name": collection_name,
        "replica_number": replica_number,
        "success": success,
        "message": f"Collection '{collection_name}' loaded successfully with {replica_number} replica(s)" if success else f"Failed to load collection '{collection_name}'"
    }


@mcp.tool()
async def milvus_release_collection(ctx: Context, collection_name: str) -> dict:
    """
    Release a collection from memory.

    Args:
        collection_name: Name of collection to release
    """
    connector = ctx.request_context.lifespan_context.connector
    success = await connector.release_collection(collection_name=collection_name)

    return {
        "collection_name": collection_name,
        "success": success,
        "message": f"Collection '{collection_name}' released successfully" if success else f"Failed to release collection '{collection_name}'"
    }


@mcp.tool()
async def milvus_list_databases(ctx: Context) -> dict:
    """List all databases in the Milvus instance."""
    connector = ctx.request_context.lifespan_context.connector
    databases = await connector.list_databases()
    return {
        "databases": databases
    }


@mcp.tool()
async def milvus_use_database(ctx: Context, db_name: str) -> dict:
    """
    Switch to a different database.

    Args:
        db_name: Name of the database to use
    """
    connector = ctx.request_context.lifespan_context.connector
    success = await connector.use_database(db_name)

    return {
        "db_name": db_name,
        "success": success,
        "message": f"Switched to database '{db_name}' successfully" if success else f"Failed to switch to database '{db_name}'"
    }


@mcp.tool()
async def milvus_get_collection_info(ctx: Context, collection_name: str) -> dict:
    """
    Lists detailed information about a specific collection

    Args:
        collection_name: Name of collection to load
    """
    connector = ctx.request_context.lifespan_context.connector
    collection_info = await connector.get_collection_info(collection_name)
    return {
        "collection_name": collection_name,
        "info": collection_info
    }

def parse_arguments():
    """Parse command line arguments with environment variable fallbacks.

    Returns:
        argparse.Namespace: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Milvus MCP Server")
    parser.add_argument("--milvus-uri", type=str, default=os.environ.get("MILVUS_URI", "http://localhost:19530"), help="Milvus server URI")
    parser.add_argument("--milvus-token", type=str, default=os.environ.get("MILVUS_TOKEN"), help="Milvus authentication token")
    parser.add_argument("--milvus-db", type=str, default=os.environ.get("MILVUS_DB", "default"), help="Milvus database name")
    parser.add_argument("--sse", action="store_true", help="Enable SSE mode")
    return parser.parse_args()


def setup_environment(args):
    """Set environment variables based on parsed arguments.
    Args:
        args (argparse.Namespace): The parsed command line arguments
    """
    os.environ["MILVUS_URI"] = args.milvus_uri
    if args.milvus_token:
        os.environ["MILVUS_TOKEN"] = args.milvus_token
    os.environ["MILVUS_DB"] = args.milvus_db


def main():
    """Main entry point for the Milvus MCP Server."""
    args = parse_arguments()
    setup_environment(args)

    if args.sse:
        mcp.run(transport="sse")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
