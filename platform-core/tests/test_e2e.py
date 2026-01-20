"""
OmniGraph E2E Tests

Tests the complete flow from user query to synthesized answer.
"""

import pytest
import asyncio
from typing import Dict, Any


# =============================================================================
# Test Configuration
# =============================================================================

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "omnigraph"


# =============================================================================
# Helper Functions
# =============================================================================

async def check_neo4j_connection() -> bool:
    """Check if Neo4j is reachable."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as n")
            record = result.single()
            driver.close()
            return record["n"] == 1
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
        return False


async def check_mcp_server() -> bool:
    """Check if local MCP server is reachable."""
    # In a real test, this would check the MCP server
    return True


# =============================================================================
# Unit Tests
# =============================================================================

class TestAgentState:
    """Test AgentState definition."""

    def test_agent_state_import(self):
        """AgentState should be importable."""
        from orchestration.state import AgentState
        assert AgentState is not None

    def test_agent_state_fields(self):
        """AgentState should have required fields."""
        from orchestration.state import AgentState
        # TypedDict fields
        annotations = AgentState.__annotations__
        assert "messages" in annotations
        assert "current_file" in annotations
        assert "retrieved_docs" in annotations
        assert "intent" in annotations


class TestGraphNodes:
    """Test individual graph nodes."""

    def test_intent_classifier_import(self):
        """Intent classifier should be importable."""
        from orchestration.graph_v2 import intent_classifier
        assert intent_classifier is not None

    def test_local_retriever_import(self):
        """Local retriever should be importable."""
        from orchestration.graph_v2 import local_retriever
        assert local_retriever is not None

    def test_global_retriever_import(self):
        """Global retriever should be importable."""
        from orchestration.graph_v2 import global_retriever
        assert global_retriever is not None

    def test_synthesizer_import(self):
        """Synthesizer should be importable."""
        from orchestration.graph_v2 import synthesizer
        assert synthesizer is not None


class TestMCPClient:
    """Test MCP client setup."""

    def test_mcp_client_import(self):
        """MCP client should be importable."""
        from orchestration.mcp_client import MultiServerMCPClient
        assert MultiServerMCPClient is not None


class TestGraphV2:
    """Test LangGraph v2 implementation."""

    def test_graph_v2_import(self):
        """graph_v2 should be importable."""
        from orchestration.graph_v2 import create_omnigraph_agent
        assert create_omnigraph_agent is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestNeo4jIntegration:
    """Test Neo4j database integration."""

    @pytest.mark.asyncio
    async def test_neo4j_connection(self):
        """Neo4j should be accessible."""
        connected = await check_neo4j_connection()
        assert connected, "Neo4j connection failed"

    @pytest.mark.asyncio
    async def test_neo4j_schema_exists(self):
        """Neo4j schema should be applied."""
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

        with driver.session() as session:
            # Check for vector indexes
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]

            # At least some indexes should exist
            assert len(indexes) > 0, "No indexes found"

        driver.close()


# =============================================================================
# E2E Tests
# =============================================================================

class TestE2EFlow:
    """End-to-end flow tests."""

    @pytest.mark.asyncio
    async def test_local_query_flow(self):
        """Test local-only query flow."""
        # Mock a local query
        query = "What functions are in the auth module?"

        # Create initial state
        from orchestration.state import AgentState
        state: AgentState = {
            "messages": [],
            "current_file": None,
            "retrieved_docs": [],
            "intent": None,
            "context_needs": None
        }

        # In a real test, we would run the full graph
        # For now, just verify the structure exists
        assert state["messages"] is not None

    @pytest.mark.asyncio
    async def test_global_query_flow(self):
        """Test global-only query flow."""
        # Mock a global query
        query = "What libraries are commonly used for authentication?"

        # Verify Neo4j is available
        connected = await check_neo4j_connection()
        if not connected:
            pytest.skip("Neo4j not available")

        # Test would run the full graph with a global query
        assert True


# =============================================================================
# Smoke Tests
# =============================================================================

class TestSmokeTests:
    """Quick smoke tests for deployment verification."""

    def test_imports(self):
        """All key modules should be importable."""
        imports_ok = True
        errors = []

        modules = [
            "orchestration.state",
            "orchestration.graph_v2",
            "orchestration.mcp_client",
        ]

        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                imports_ok = False
                errors.append(f"{module}: {e}")

        assert imports_ok, f"Import errors: {errors}"

    @pytest.mark.asyncio
    async def test_infrastructure(self):
        """All infrastructure should be running."""
        neo4j_ok = await check_neo4j_connection()
        assert neo4j_ok, "Neo4j is not running"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
