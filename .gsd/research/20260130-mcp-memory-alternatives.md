# Research Report: MemoryGraph Alternatives

This report analyzes potential alternatives to `memory-graph` for providing long-term memory and knowledge graph capabilities to AI agents via MCP.

## Top Recommendations

### 1. Official MCP Memory Server (`@modelcontextprotocol/server-memory`)
> **Best for:** Users seeking a lightweight, standard-compliant solution.

- **Description**: The official reference implementation for knowledge graph-based persistent memory.
- **Type**: Knowledge Graph (Local)
- **Status**: Official Reference
- **Pros**:
    - Zero configuration (works out of the box with `npx`).
    - Lightweight and follows official MCP standards strictly.
    - Open source and maintained by the MCP community/Anthropic.
- **Cons**:
    - Generic implementation (not specialized for coding tasks like `memory-graph`).
    - Less feature-rich compared to specialized tools (e.g., no git integration).
- **Setup**:
  ```json
  "curr_memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
  ```

### 2. Mem0 (`mem0ai/mem0-mcp`)
> **Best for:** User retrieval, personaliztion, and **Semantic Search**.

- **Description**: A memory layer for AI agents that optimizes for personalization using vector stores and graphs.
- **Type**: Hybrid (Vector + Graph) linked to LLMs.
- **Embedding Support**: **Excellent**.
    - Native support for vector databases (Qdrant, Chroma, Pgvector).
    - Can use local embedding models (via Ollama/LocalAI) or APIs (OpenAI).
    - Semantic search is a core feature (`search_memories`).
- **Pros**:
    - Strong focus on "User Memory" (preferences, facts).
    - Intelligent retrieval (Hybrid Search).
    - Supports various backends (Qdrant, Redis, Postgres).
- **Cons**:
    - Setup is more complex (requires API keys, vector DB setup).
    - May be overkill if you just need simple graph relations.
- **Setup**: Requires Docker or Python package installation + API configuration.

### 3. Zep (Graphiti)
> **Best for:** Complex agents needing temporal context and deep memory management.

- **Description**: Zep is a long-term memory service for AI. Its underlying engine, **Graphiti**, creates temporal knowledge graphs.
- **Type**: Temporal Knowledge Graph.
- **Embedding Support**: **Good** (Hybrid).
    - Zep Cloud handles embeddings automatically.
    - Graphiti (open source) supports vector search via Neo4j/FalkorDB integration.
- **Pros**:
    - **Temporal Awareness**: Understands *when* facts changed.
    - Production-grade scalability (Zep Cloud).
    - Excellent for conversational agents.
- **Cons**:
    - Heavily oriented towards "Conversational Memory" rather than "Codebase Memory".
    - Often requires a cloud service or heavy local infrastructure (Neo4j).

### 4. Neo4j MCP (`mcp-neo4j-memory`)
> **Best for:** Enterprise-grade graph database requirements and full control.

- **Description**: Uses Neo4j as the backend for storing agent memories.
- **Type**: Property Graph Database.
- **Embedding Support**: **Supported** (via Neo4j Vector Index).
    - Requires setting up Neo4j Vector Indexes manually or via specific plugins.
    - MCP tools for vector search might need extra configuration.
- **Pros**:
    - Extremely powerful query language (Cypher).
    - Mature ecosystem and visualization tools (Neo4j Browser).
    - Full data ownership and scalability.
- **Cons**:
    - Heavyweight (requires running a Neo4j instance).
    - Higher learning curve for configuration.

## Comparison with MemoryGraph

| Feature | MemoryGraph | Official Memory Server | Mem0 | Neo4j MCP |
| :--- | :--- | :--- | :--- | :--- |
| **Focus** | Coding Agents (Git, Code Patterns) | Generic Knowledge Graph | User Personalization | General Graph Data |
| **Backend** | SQLite / FalkorDB | JSON / SQLite (Simple) | **Vector DB** / Graph | Neo4j |
| **Embedding**| ❌ No (LLM Context only) | ❌ No | **✅ Yes (Core)** | ✅ Yes (Index) |
| **Setup** | Moderate (pipx / npx) | Easy (npx) | Complex (Docker/API) | Complex (DB Instance) |
| **Code Aware** | ✅ High (Git hooks, etc.) | ❌ Low | ❌ Low | ❌ Low |

### 5. BeaconBay/ck (`BeaconBay/ck`)
> **Best for:** High-performance local semantic code search.

- **Description**: A local-first semantic and hybrid (BM25 + Embedding) code search tool with native MCP support.
- **Type**: Semantic Code Search Engine.
- **Embedding Support**: **Excellent (Local First)**.
    - Uses `ort` (ONNX Runtime) for local embedding generation.
    - Supports hybrid search (Keyword + Semantic).
    - Automatic delta indexing with chunk-level caching.
- **Pros**:
    - **Fast & Local**: Optimized for performance with Rust.
    - **Drop-in Grep**: Can be used as a CLI tool as well as an MCP server.
    - **Hybrid Search**: Combines exact keyword matching with semantic understanding.
    - **Zero Config**: "Just works" mentality for local setups.
- **Cons**:
    - Focuses on **Code Search** (finding code) rather than **Agent Memory** (remembering plans/facts).
    - Less about "long-term memory" and more about "codebase access".

## Comparison with MemoryGraph

| Feature | MemoryGraph | Mem0 | BeaconBay/ck |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Agent Long-term Memory | User Personalization | **Semantic Code Search** |
| **Data Source** | Abstracted Facts/Graphs | User Interactions | **Actual Codebase** |
| **Embedding**| ❌ No (LLM Context) | ✅ Yes (User Data) | **✅ Yes (Local Code)** |
| **Search** | Graph Traversal | Vector/Hybrid | **Hybrid (BM25+Vector)** |
| **Speed** | Moderate | Moderate | **High (Rust)** |

## Conclusion

### Final Recommendation

1.  **For Searching Your Codebase (User's likely intent for "Embeddings"):**
    - **`BeaconBay/ck` is the best choice.** It replaces `code-graph-rag` effectively for finding code using natural language queries. It runs locally, uses embeddings, and is fast.

2.  **For Remembering Plans & Decisions:**
    - Stick with **`memory-graph`** or use **`@modelcontextprotocol/server-memory`**. `ck` finds code, it doesn't "remember" that you decided to use a specific pattern last week unless you wrote it in a comment.

3.  **For User Preferences:**
    - Use **Mem0**.

**Actionable Advice:**
If your goal is "I want to ask the agent about my code using embeddings" (e.g., "Where is the authentication logic?"), switch to **`BeaconBay/ck`**.

