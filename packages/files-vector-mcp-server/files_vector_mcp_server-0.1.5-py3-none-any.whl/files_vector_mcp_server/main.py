import os
import logging
import time
import asyncio
import threading
from typing import Optional, Dict, List
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局服务实例
db_service = None
file_processor = None
config = None
observer = None  # 文件监控器实例
worker_threads = []  # 工作线程列表，用于优雅关闭


def main():
    """非异步主函数，完全遵循FastMCP官方示例"""
    global db_service, file_processor, config, observer

    try:
        # 加载环境变量和配置（同步方式）
        load_config()

        # 初始化核心服务（同步方式）
        initialize_services()

        # 启动全局事件循环
        from .utils import start_worker_event_loop
        start_worker_event_loop()

        # 创建FastMCP实例（完全按照官方示例）
        mcp = FastMCP(name="file-vector-server")

        # 注册工具（使用显式参数）
        register_tools(mcp)

        # 启动文件监控（在FastMCP实例创建后启动）
        start_file_watcher()

        # 启动服务器（官方示例的标准方式）
        logger.info("FastMCP文件向量服务器启动中...")
        mcp.run()  # 不使用await或asyncio

    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        return
    finally:
        # 确保所有资源正确停止
        if observer and observer.is_alive():
            observer.stop()
            observer.join()
            logger.info("文件监控器已停止")

        # 停止所有工作线程
        for thread in worker_threads:
            if thread.is_alive():
                thread.join(timeout=5)
                logger.info(f"工作线程 {thread.name} 已停止")

        # 停止事件循环
        from .utils import stop_worker_event_loop
        stop_worker_event_loop()


def load_config():
    """同步加载配置"""
    global config
    from .config.settings import Config

    # 加载.env文件（同步方式）
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("已从.env文件加载环境变量")
    except ImportError:
        pass

    # 创建配置（同步方式）
    config = Config.from_cli()

    # 打印监控目录信息
    watch_dirs = config.all_watch_directories
    logger.info(f"当前监控目录: {watch_dirs}")
    logger.info(f"分块配置: 大小={config.chunk_size}, 重叠={config.chunk_overlap}")


def initialize_services():
    """同步初始化核心服务"""
    global db_service, file_processor, config

    # 初始化数据库服务（同步方式）
    from .services.database import VectorDB
    db_service = VectorDB(
        connection_string=config.db_connection_string,
        embedding_dim=config.embedding_dim
    )

    # 添加数据库连接测试
    try:
        with db_service._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                if result:
                    logger.info("数据库连接测试成功")
                else:
                    logger.error("数据库连接测试失败")
                    raise Exception("数据库连接测试失败")
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        raise

    # 初始化OpenAI客户端（同步方式）
    from openai import OpenAI
    openai_client = OpenAI(
        api_key=config.openai_api_key,
        base_url=config.openai_api_url
    )

    # 验证OpenAI连接
    try:
        openai_client.models.list()
        logger.info("OpenAI API连接测试成功")
    except Exception as e:
        logger.error(f"OpenAI API连接测试失败: {e}")
        raise

    # 初始化文件处理器（同步方式）
    from .services.file_processor import FileProcessor
    file_processor = FileProcessor(
        db_service=db_service,
        openai_client=openai_client,
        config=config
    )


def register_tools(mcp: FastMCP):
    """注册工具，使用显式参数而非params字典"""

    # 注册get_stats工具（显式参数）
    @mcp.tool
    def get_stats(
            file_path: Optional[str] = None,
            topic: Optional[str] = None
    ) -> dict:
        """获取文件处理状态统计"""
        global db_service
        try:
            if file_path:
                status = db_service.get_file_status(file_path)
                if not status:
                    return {"status": "error", "message": "文件未找到"}
                return {"status": "success", "data": status}
            else:
                stats = db_service.get_file_status(topic=topic)
                return {"status": "success", "data": stats}

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"status": "error", "message": str(e)}

    # 注册search工具（合并read_chunk功能）
    @mcp.tool
    def search(
            query: str,
            top_k: int = 5,
            topic: Optional[str] = None,
            file_path: Optional[str] = None,
            return_content: bool = False  # 新增参数：是否返回完整内容
    ) -> dict:
        """搜索文件内容（块级搜索），支持返回完整块内容"""
        global db_service, file_processor, config
        try:
            if not query:
                return {"status": "error", "message": "查询参数是必需的"}

            # 生成查询向量
            query_vector = file_processor._get_embedding_with_retry(query)

            # 块级向量搜索
            results = db_service.search_similar_chunks(
                query_vector,
                top_k,
                topic=topic,
                file_path=file_path
            )

            # 如果需要返回完整内容
            if return_content:
                for result in results:
                    chunk = db_service.get_chunk_by_id(result["chunk_id"])
                    result["content"] = chunk["content"]

            return {"status": "success", "data": results}

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"status": "error", "message": str(e)}

    # 注册read_file工具
    @mcp.tool
    def read_file(file_path: str, max_chars: int = 8000) -> dict:
        """读取完整文件内容（带长度限制）"""
        try:
            # 验证文件路径是否在监控目录中
            from .utils import get_all_watch_directories
            watch_dirs = get_all_watch_directories(config.watch_topics)
            is_allowed = any(file_path.startswith(dir) for dir in watch_dirs)

            if not is_allowed:
                return {"status": "error", "message": "Access denied: file not in monitored directories"}

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 处理长内容
            truncated = False
            original_length = len(content)

            if original_length > max_chars:
                content = content[:max_chars]
                truncated = True

            return {
                "status": "success",
                "data": {
                    "file_path": file_path,
                    "content": content,
                    "truncated": truncated,
                    "original_length": original_length,
                    "returned_length": len(content),
                    "max_chars": max_chars
                }
            }
        except FileNotFoundError:
            return {"status": "error", "message": "File not found"}
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return {"status": "error", "message": str(e)}

    # 注册create_markdown工具
    @mcp.tool
    def create_markdown(file_path: str, content: str) -> dict:
        """创建markdown文件并自动触发向量化"""
        global config
        try:
            # 验证文件路径是否在监控目录中
            from .utils import get_all_watch_directories
            watch_dirs = get_all_watch_directories(config.watch_topics)
            is_allowed = any(file_path.startswith(dir) for dir in watch_dirs)

            if not is_allowed:
                return {"status": "error", "message": "Access denied: file path not in monitored directories"}

            # 确保目录存在
            dir_name = os.path.dirname(file_path)
            os.makedirs(dir_name, exist_ok=True)

            # 写入文件内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"已创建文件: {file_path}")

            # 触发文件处理（添加到任务队列）
            from .start_file_watcher import task_queue  # 导入任务队列
            task_queue.put((file_path, "created", None))

            return {
                "status": "success",
                "data": {
                    "file_path": file_path,
                    "created": True,
                    "size": len(content),
                    "auto_vectorization": True,
                    "message": "文件已创建，将自动进行向量化处理"
                }
            }
        except Exception as e:
            logger.error(f"创建文件失败: {e}")
            return {"status": "error", "message": str(e)}


def start_file_watcher():
    """同步启动文件监控"""
    global config, observer, worker_threads

    # 创建全局事件队列
    from .utils import event_queue

    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from queue import Queue

    from .utils import get_all_watch_directories, is_supported_file_type

    # 创建任务队列（全局可见，供create_markdown使用）
    global task_queue
    task_queue = Queue(maxsize=config.batch_size * 10)
    logger.info(f"任务队列初始化完成，最大容量: {config.batch_size * 10}")

    class FileChangeHandler(FileSystemEventHandler):
        """文件变化处理器"""

        def on_modified(self, event):
            self._handle_event(event)

        def on_created(self, event):
            self._handle_event(event)

        def on_moved(self, event):
            if not event.is_directory and any(
                    event.dest_path.startswith(dir) for dir in get_all_watch_directories(config.watch_topics)):
                logger.info(f"文件移动: {event.src_path} -> {event.dest_path}")
                task_queue.put((event.dest_path, "moved", event.src_path))

        def _handle_event(self, event):
            if event.is_directory:
                return

            file_path = os.path.abspath(event.src_path)
            watch_dirs = get_all_watch_directories(config.watch_topics)

            # 详细日志
            if any(file_path.startswith(dir) for dir in watch_dirs):
                logger.debug(f"文件 {file_path} 在监控目录下")
                if is_supported_file_type(file_path):
                    logger.debug(f"文件 {file_path} 是支持的类型")
                    if not os.path.basename(file_path).startswith(".") and not file_path.endswith("~"):
                        logger.info(f"检测到文件变化: {file_path}")
                        task_queue.put((file_path, "modified", None))
                        logger.info(f"文件 {file_path} 已添加到任务队列，当前队列大小: {task_queue.qsize()}")
                    else:
                        logger.debug(f"忽略临时文件或隐藏文件: {file_path}")
                else:
                    logger.debug(f"文件 {file_path} 是不支持的类型")
            else:
                logger.debug(f"文件 {file_path} 不在监控目录下")

    # 创建事件处理器和监控器
    event_handler = FileChangeHandler()
    observer = Observer()

    # 为每个监控目录添加监控
    for directory in get_all_watch_directories(config.watch_topics):
        observer.schedule(event_handler, directory, recursive=True)
        logger.info(f"已添加监控目录: {directory}")

    # 启动监控器
    observer.start()
    logger.info(f"已启动文件监控，监控目录数: {len(get_all_watch_directories(config.watch_topics))}")

    # 初始扫描文件
    def initial_scan():
        """初始扫描所有监控目录中的文件"""
        file_count = 0
        for directory in get_all_watch_directories(config.watch_topics):
            logger.info(f"开始扫描目录: {directory}")
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if is_supported_file_type(file_path):
                        task_queue.put((file_path, "modified", None))
                        file_count += 1
                        # 进度日志
                        if file_count % 10 == 0:
                            logger.info(f"初始扫描已发现 {file_count} 个文件")
        logger.info(f"初始扫描完成，发现 {file_count} 个支持的文件需要处理")
        logger.info(f"任务队列当前大小: {task_queue.qsize()}")

        # 如果没有发现文件，发出警告
        if file_count == 0:
            logger.warning("初始扫描未发现任何支持的文件，请检查监控目录和文件类型")

    # 启动初始扫描线程
    initial_scan_thread = threading.Thread(target=initial_scan, name="InitialScanThread")
    initial_scan_thread.start()
    worker_threads.append(initial_scan_thread)
    logger.info("初始扫描线程已启动")

    # 启动批处理工作线程
    def batch_worker():
        """批处理工作线程"""
        global file_processor, config

        logger.info(f"批处理工作线程启动（批大小: {config.batch_size}）")
        while True:
            try:
                batch = []
                for _ in range(config.batch_size):
                    try:
                        item = task_queue.get(timeout=1)
                        batch.append(item)
                    except Exception:
                        break

                if batch:
                    logger.info(f"处理批次: {len(batch)} 个文件")
                    file_paths = [item[0] for item in batch]

                    # 添加处理前日志
                    for file_path in file_paths:
                        logger.info(f"准备处理文件: {file_path}")

                    file_processor.process_batch(file_paths)

                    # 标记批次中所有任务为完成
                    for item in batch:
                        task_queue.task_done()

                    logger.info(f"批次处理完成，剩余队列大小: {task_queue.qsize()}")

                # 短暂休眠
                time.sleep(1)

            except Exception as e:
                logger.error(f"批处理工作线程错误: {e}", exc_info=True)
                # 记录详细异常信息
                event_data = {
                    "type": "error_occurred",
                    "component": "batch_worker",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

                # 使用全局事件循环发送事件
                from .utils import get_event_loop
                loop = get_event_loop()
                if loop and loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        event_queue.put(event_data),
                        loop
                    )
                else:
                    logger.error("无法发送事件：全局事件循环未运行")

    # 启动批处理工作线程
    batch_worker_thread = threading.Thread(target=batch_worker, name="BatchWorkerThread")
    batch_worker_thread.start()
    worker_threads.append(batch_worker_thread)
    logger.info("批处理工作线程已启动")


# 辅助函数
def get_all_watch_directories(watch_topics):
    """获取所有监控目录"""
    directories = []
    for topic, dirs in watch_topics.items():
        directories.extend(dirs)
    return [os.path.abspath(d) for d in directories]


# 官方示例风格的入口点
if __name__ == "__main__":
    main()