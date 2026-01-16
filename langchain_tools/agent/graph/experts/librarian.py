from typing import Literal
from langchain_core.messages import SystemMessage
from langgraph.types import Command
from langgraph.graph import END

from langchain_tools.agent.graph.state import AgentState
from langchain_tools.tools.claude_knowledge import ClaudeKnowledgeUpdaterTool
from langchain_tools.agent.background_manager import background_manager

def librarian_node(state: AgentState) -> Command[Literal["__end__"]]:
    """
    Knowledge Librarian Agent.

    Responsibilities:
    1. Summarize task success.
    2. Update CLAUDE.md with Lessons Learned (Background Task).
    3. Terminate the graph execution immediately.
    """
    print("📚 [Librarian] Submitting Knowledge Update (Background)...")

    changed_files = state.get("changed_files", [])
    intent_path = state.get("intent_path")

    # Define the update function (to be run in background)
    def update_claude_knowledge(verification_data: dict):
        print(f"   ⏳ [Background] Updating CLAUDE.md for {verification_data['intent']}...")
        updater = ClaudeKnowledgeUpdaterTool()
        try:
            updater.invoke({"verification_result": verification_data})
            return "CLAUDE.md updated successfully"
        except Exception as e:
            raise e

    # Prepare data
    verification_result = {
        "steps": {
            "approve": {"status": "approved"},
            "verify": {
                "basic": {"errors": []},
                "security": {"status": "secure"}
            }
        },
        "intent": intent_path,
        "changed_files": changed_files
    }

    # === PHASE 3: Background Execution ===
    # Submit task and don't wait for result
    try:
        task_id = f"librarian_update_{state.get('task_id', 'unknown')}"
        # create_task wrapper for sync function
        import asyncio
        asyncio.create_task(background_manager.submit_task(
            update_claude_knowledge,
            verification_data=verification_result,
            task_id=task_id
        ))
        print(f"   🚀 [Librarian] Task submitted: {task_id}")
    except Exception as e:
        print(f"   ⚠️ Background submission failed: {e}")
        # Fallback sync
        update_claude_knowledge(verification_result)

    return Command(
        update={
            "messages": [SystemMessage(content=f"Knowledge update scheduled. Task Completed.")],
            "next_agent": "END"
        },
        goto=END
    )
