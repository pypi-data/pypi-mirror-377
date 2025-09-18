import asyncio
import threading
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 全局事件队列
event_queue = asyncio.Queue()

# 全局事件循环和线程
_worker_loop: Optional[asyncio.AbstractEventLoop] = None
_loop_thread: Optional[threading.Thread] = None

async def process_events():
    """处理事件队列中的事件"""
    while True:
        try:
            event = await event_queue.get()
            # 这里可以添加事件处理逻辑
            event_queue.task_done()
        except Exception as e:
            logger.error(f"事件处理错误: {e}")

def get_event_loop() -> asyncio.AbstractEventLoop:
    """获取全局事件循环，确保在所有线程中使用同一个循环"""
    global _worker_loop
    if _worker_loop is None:
        raise RuntimeError("事件循环尚未初始化，请先调用start_worker_event_loop()")
    return _worker_loop

def start_worker_event_loop():
    """启动工作线程事件循环"""
    global _worker_loop, _loop_thread
    
    if _loop_thread is not None and _loop_thread.is_alive():
        logger.warning("事件循环线程已在运行中")
        return
    
    # 创建新的事件循环
    _worker_loop = asyncio.new_event_loop()
    
    # 创建并启动事件循环线程
    def loop_runner():
        asyncio.set_event_loop(_worker_loop)
        try:
            _worker_loop.run_until_complete(process_events())
        except Exception as e:
            logger.error(f"事件循环线程异常终止: {e}")
    
    _loop_thread = threading.Thread(target=loop_runner, name="EventLoopThread", daemon=True)
    _loop_thread.start()
    
    # 等待循环初始化完成
    while _worker_loop is None or not _worker_loop.is_running():
        time.sleep(0.1)
    
    logger.info("事件循环线程已启动")

def stop_worker_event_loop():
    """停止工作线程事件循环"""
    global _worker_loop, _loop_thread
    
    if _worker_loop is not None and _worker_loop.is_running():
        _worker_loop.call_soon_threadsafe(_worker_loop.stop)
    
    if _loop_thread is not None and _loop_thread.is_alive():
        _loop_thread.join()
    
    _worker_loop = None
    _loop_thread = None
    logger.info("事件循环线程已停止")