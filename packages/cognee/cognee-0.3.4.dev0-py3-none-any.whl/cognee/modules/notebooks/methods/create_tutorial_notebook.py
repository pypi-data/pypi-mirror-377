from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import NotebookCell
from .create_notebook import create_notebook


async def create_tutorial_notebook(user_id: UUID, session: AsyncSession):
    await create_notebook(
        user_id=user_id,
        notebook_name="Welcome to cognee 🧠",
        cells=[
            NotebookCell(
                id=uuid4(),
                name="Welcome",
                content="Cognee is your toolkit for turning text into a structured knowledge graph, optionally enhanced by ontologies, and then querying it with advanced retrieval techniques. This notebook will guide you through a simple example.",
                type="markdown",
            ),
            NotebookCell(
                id=uuid4(),
                name="Example",
                content="",
                type="markdown",
            ),
        ],
        deletable=False,
        session=session,
    )


cell_content = [
    """
# Using Cognee with Python Development Data

Unite authoritative Python practice (Guido van Rossum's own contributions!), normative guidance (Zen/PEP 8), and your lived context (rules + conversations) into one *AI memory* that produces answers that are relevant, explainable, and consistent.
""",
    """
## What You'll Learn

In this comprehensive tutorial, you'll discover how to transform scattered development data into an intelligent knowledge system that enhances your coding workflow. By the end, you'll have:
- Connected disparate data sources (Guido's CPython contributions, mypy development, PEP discussions, your Python projects) into a unified AI memory graph
- Built an memory layer that understands Python design philosophy, best practice coding patterns, and your preferences and experience
- Learn how to use intelligent search capabilities that combine the diverse context
- Integrated everything with your coding environment through MCP (Model Context Protocol)

This tutorial demonstrates the power of **knowledge graphs** and **retrieval-augmented generation (RAG)** for software development, showing you how to build systems that learn from Python's creator and improve your own Python development.
""",
    """
## Cognee and its core operations

Before we dive in, let's understand the core Cognee operations we'll be working with:
- `cognee.add()` - Ingests raw data (files, text, APIs) into the system
- `cognee.cognify()` - Processes and structures data into a knowledge graph using AI
- `cognee.search()` - Queries the knowledge graph with natural language or Cypher
- `cognee.memify()` - Cognee's \"secret sauce\" that infers implicit connections and rules from your data
""",
    """
## Data used in this tutorial

Cognee can ingest many types of sources. In this tutorial, we use a small, concrete set of files that cover different perspectives:
- `guido_contributions.json` — Authoritative exemplars. Real PRs and commits from Guido van Rossum (mypy, CPython). These show how Python's creator solved problems and provide concrete anchors for patterns.
- `pep_style_guide.md` — Norms. Encodes community style and typing conventions (PEP 8 and related). Ensures that search results and inferred rules align with widely accepted standards.
- `zen_principles.md` — Philosophy. The Zen of Python. Grounds design trade-offs (simplicity, explicitness, readability) beyond syntax or mechanics.
- `my_developer_rules.md` — Local constraints. Your house rules, conventions, and project-specific requirements (scope, privacy, Spec.md). Keeps recommendations relevant to your actual workflow.
- `copilot_conversations.json` — Personal history. Transcripts of real assistant conversations, including your questions, code snippets, and discussion topics. Captures "how you code" and connects it to "how Guido codes."
""",
    """
# Preliminaries

To strike the balanace between speed, cost, anc quality, we recommend using OpenAI's `4o-mini` model; make sure your `.env` file contains this line:
`
LLM_MODEL="gpt-4o-mini"
`
""",
    """
import cognee

result = await cognee.add(
    "file://data/guido_contributions.json",
    node_set=["guido_data"]
)

await cognee.cognify(temporal_cognify=True)

results = await cognee.search("Show me commits")
""",
]
