"""全局任务队列管理"""
import logging
from queue import Queue
from typing import Any

logger = logging.getLogger(__name__)

# 全局任务队列实例
_task_queue = None

def init_task_queue(maxsize: int = 0) -> None:
    """初始化任务队列"""
    global _task_queue
    if _task_queue is None:
        _task_queue = Queue(maxsize=maxsize)
        logger.info(f"任务队列初始化完成，最大容量: {maxsize}")

def get_task_queue() -> Queue[Any]:
    """获取任务队列实例"""
    global _task_queue
    if _task_queue is None:
        raise RuntimeError("任务队列尚未初始化，请先调用init_task_queue()")
    return _task_queue

def put_task(item: Any) -> None:
    """添加任务到队列"""
    queue = get_task_queue()
    queue.put(item)
    logger.debug(f"任务已添加到队列，当前队列大小: {queue.qsize()}")