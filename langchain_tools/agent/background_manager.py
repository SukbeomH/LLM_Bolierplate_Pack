"""Background Task Manager.

Uses Python's built-in asyncio and concurrent.futures to manage background tasks
without external dependencies like Celery or Redis.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable, Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Free background task manager using Python built-ins."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BackgroundTaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_workers: int = 4):
        if not hasattr(self, 'executor'):
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.tasks: Dict[str, asyncio.Task] = {}
            self.results: Dict[str, Any] = {}

    async def submit_task(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Submit a task to be executed in the background.

        Args:
            func: The function to execute (can be sync or async)
            *args: Positional arguments for the function
            task_id: Optional custom task ID
            **kwargs: Keyword arguments for the function

        Returns:
            task_id: The ID of the submitted task
        """
        if not task_id:
            task_id = str(uuid.uuid4())

        loop = asyncio.get_running_loop()

        if asyncio.iscoroutinefunction(func):
            # It's an async function, wrap straight into a task
            coro = func(*args, **kwargs)
            task = asyncio.create_task(self._wrap_async_task(task_id, coro))
        else:
            # It's a sync function, run in thread pool
            # We wrap the thread execution in an asyncio task to track it
            task = asyncio.create_task(
                self._wrap_sync_task(loop, task_id, func, *args, **kwargs)
            )

        self.tasks[task_id] = task
        logger.info(f"Background task {task_id} submitted")
        return task_id

    async def _wrap_async_task(self, task_id: str, coro):
        """Wrapper for async coroutines."""
        try:
            result = await coro
            self._complete_task(task_id, result)
        except Exception as e:
            self._fail_task(task_id, e)

    async def _wrap_sync_task(self, loop, task_id: str, func, *args, **kwargs):
        """Wrapper for synchronous functions running in thread pool."""
        try:
            from functools import partial
            # run_in_executor doesn't support kwargs directly, so we use partial
            p_func = partial(func, *args, **kwargs)
            result = await loop.run_in_executor(self.executor, p_func)
            self._complete_task(task_id, result)
        except Exception as e:
            self._fail_task(task_id, e)

    def _complete_task(self, task_id: str, result: Any):
        """Mark task as completed."""
        self.results[task_id] = {
            "status": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        # Cleanup task reference but keep result
        if task_id in self.tasks:
            del self.tasks[task_id]
        logger.info(f"Background task {task_id} completed")

    def _fail_task(self, task_id: str, error: Exception):
        """Mark task as failed."""
        self.results[task_id] = {
            "status": "failed",
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }
        if task_id in self.tasks:
            del self.tasks[task_id]
        logger.error(f"Background task {task_id} failed: {error}")

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        # Check running tasks
        if task_id in self.tasks:
            return {"status": "running"}

        # Check completed/failed results
        if task_id in self.results:
            return self.results[task_id]

        return {"status": "not_found"}

# Global instance
background_manager = BackgroundTaskManager()
