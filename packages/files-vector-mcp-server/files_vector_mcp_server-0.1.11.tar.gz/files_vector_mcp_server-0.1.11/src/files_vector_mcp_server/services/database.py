import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class VectorDB:
    """向量数据库服务类，处理文件向量和分块向量的存储和查询"""

    def __init__(self, connection_string: str, embedding_dim: int):
        """初始化数据库连接和表结构"""
        self.connection_string = connection_string
        self.embedding_dim = embedding_dim
        self._create_tables()

    def _get_connection(self):
        """获取数据库连接"""
        import psycopg2
        return psycopg2.connect(self.connection_string)

    def _create_tables(self):
        """创建必要的数据库表和索引"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 启用pgvector扩展
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                    # 创建文件表
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS files (
                        id SERIAL PRIMARY KEY,
                        file_path TEXT UNIQUE NOT NULL,
                        topic TEXT NOT NULL,
                        file_hash TEXT NOT NULL,
                        last_modified TIMESTAMP NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        error_message TEXT,
                        total_chunks INTEGER DEFAULT 0,
                        processed_chunks INTEGER DEFAULT 0,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

                    # 创建块表
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id SERIAL PRIMARY KEY,
                        file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
                        chunk_num INTEGER NOT NULL,
                        total_chunks INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        vector vector({self.embedding_dim}) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(file_id, chunk_num)
                    );
                    """)

                    # 创建索引
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_file_path ON files(file_path);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_topic ON files(topic);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);")
                    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id);")
                    cur.execute(
                        f"CREATE INDEX IF NOT EXISTS idx_chunks_vector ON chunks USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);")

                    conn.commit()
                    logger.info(f"数据库表结构初始化成功（向量维度: {self.embedding_dim}）")

        except Exception as e:
            logger.error(f"创建数据库表结构失败: {e}")
            raise

    def upsert_file(self,
                    file_path: str,
                    topic: str,
                    file_hash: str,
                    last_modified: datetime,
                    status: str,
                    total_chunks: int = 0,
                    processed_chunks: int = 0,
                    error_message: Optional[str] = None) -> int:
        """插入或更新文件信息（不含向量，向量存储在块表中）"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 先执行UPSERT获取文件ID
                    cur.execute("""
                    INSERT INTO files (file_path, topic, file_hash, last_modified, status, 
                                      total_chunks, processed_chunks, error_message, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (file_path) DO UPDATE SET
                        topic = EXCLUDED.topic,
                        file_hash = EXCLUDED.file_hash,
                        last_modified = EXCLUDED.last_modified,
                        status = EXCLUDED.status,
                        total_chunks = EXCLUDED.total_chunks,
                        processed_chunks = EXCLUDED.processed_chunks,
                        error_message = EXCLUDED.error_message,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id;
                    """, (file_path, topic, file_hash, last_modified, status,
                          total_chunks, processed_chunks, error_message))

                    file_id = cur.fetchone()[0]
                    conn.commit()

                    # 发送状态更新事件
                    from ..utils.events import event_queue, get_event_loop
                    event_data = {
                        "type": "status_updated",
                        "file_path": file_path,
                        "topic": topic,
                        "status": status,
                        "total_chunks": total_chunks,
                        "processed_chunks": processed_chunks,
                        "timestamp": datetime.now().isoformat()
                    }
                    if error_message:
                        event_data["error"] = error_message

                    asyncio.run_coroutine_threadsafe(
                        event_queue.put(event_data),
                        get_event_loop()
                    )

                    return file_id

        except Exception as e:
            logger.error(f"更新文件 {file_path} 到数据库失败: {e}")
            raise

    def upsert_chunk(self,
                     file_id: int,
                     chunk_num: int,
                     total_chunks: int,
                     content: str,
                     vector: List[float]) -> bool:
        """插入或更新文件块向量"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 插入或更新块记录
                    cur.execute("""
                    INSERT INTO chunks (file_id, chunk_num, total_chunks, content, vector, updated_at)
                    VALUES (%s, %s, %s, %s, %s::vector, CURRENT_TIMESTAMP)
                    ON CONFLICT (file_id, chunk_num) DO UPDATE SET
                        total_chunks = EXCLUDED.total_chunks,
                        content = EXCLUDED.content,
                        vector = EXCLUDED.vector,
                        updated_at = CURRENT_TIMESTAMP;
                    """, (file_id, chunk_num, total_chunks, content, vector))

                    # 更新文件的已处理块数
                    cur.execute("""
                    UPDATE files 
                    SET processed_chunks = (SELECT COUNT(*) FROM chunks WHERE file_id = %s),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """, (file_id, file_id))

                    conn.commit()
                    logger.debug(f"文件块 {file_id}:{chunk_num}/{total_chunks} 已更新到数据库")
                    return True

        except Exception as e:
            logger.error(f"更新文件块 {file_id}:{chunk_num} 失败: {e}")
            raise

    def get_file_status(self, file_path: Optional[str] = None, topic: Optional[str] = None) -> Any:
        """获取文件处理状态统计"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    if file_path:
                        cur.execute("""
                        SELECT f.id, f.file_path, f.topic, f.status, f.last_modified, f.updated_at,
                               f.total_chunks, f.processed_chunks, f.error_message
                        FROM files f
                        WHERE f.file_path = %s;
                        """, (file_path,))

                        result = cur.fetchone()
                        if result:
                            return {
                                "id": result[0],
                                "file_path": result[1],
                                "topic": result[2],
                                "status": result[3],
                                "last_modified": result[4].isoformat(),
                                "last_processed": result[5].isoformat(),
                                "total_chunks": result[6],
                                "processed_chunks": result[7],
                                "error_message": result[8]
                            }
                        return None
                    else:
                        query = """
                        SELECT topic, status, COUNT(*) as count, MAX(updated_at) as last_updated,
                               SUM(total_chunks) as total_chunks, SUM(processed_chunks) as processed_chunks
                        FROM files
                        """
                        params = []

                        if topic:
                            query += " WHERE topic = %s"
                            params.append(topic)

                        query += " GROUP BY topic, status;"
                        cur.execute(query, params)
                        results = cur.fetchall()

                        stats = {}
                        for topic_name, status, count, last_updated, total_chunks, processed_chunks in results:
                            if topic_name not in stats:
                                stats[topic_name] = {}
                            stats[topic_name][status] = {
                                "count": count,
                                "total_chunks": total_chunks or 0,
                                "processed_chunks": processed_chunks or 0,
                                "last_updated": last_updated.isoformat() if last_updated else None
                            }

                        return stats

        except Exception as e:
            logger.error(f"获取文件状态失败: {e}")
            raise

    def search_similar_chunks(self, query_vector: List[float], top_k: int = 5,
                              topic: Optional[str] = None, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """向量相似度搜索（块级）"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 基础查询 - 连接文件和块表，添加向量类型转换
                    query = """
                    SELECT c.id, c.file_id, f.file_path, f.topic, c.chunk_num, c.total_chunks, 
                           1 - (c.vector <=> %s::vector) as similarity, c.content, f.last_modified
                    FROM chunks c
                    JOIN files f ON c.file_id = f.id
                    WHERE f.status = 'success'
                    """
                    # 初始化参数列表，先添加查询向量
                    params = [query_vector]

                    # 添加主题过滤
                    if topic:
                        query += " AND f.topic = %s"
                        params.append(topic)

                    # 添加文件路径过滤
                    if file_path:
                        query += " AND f.file_path = %s"
                        params.append(file_path)

                    # 添加排序和限制条件
                    query += " ORDER BY c.vector <=> %s::vector LIMIT %s;"
                    # 添加排序向量和top_k参数
                    params.append(query_vector)
                    params.append(top_k)

                    # 执行查询
                    cur.execute(query, params)
                    results = cur.fetchall()

                    # 处理结果 - 检查是否为空
                    if not results:
                        logger.info("搜索未找到匹配结果")
                        return []

                    # 构建结果 - 包含块内容预览
                    return [
                        {
                            "chunk_id": res[0],
                            "file_id": res[1],
                            "file_path": res[2],
                            "topic": res[3],
                            "chunk_num": res[4],
                            "total_chunks": res[5],
                            "similarity": float(res[6]),
                            "content_preview": res[7][:200] + "..." if len(res[7]) > 200 else res[7],
                            "last_modified": res[8].isoformat()
                        } for res in results
                    ]

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """根据chunk_id获取完整块内容"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT c.id, c.chunk_num, c.total_chunks, c.content, f.file_path
                    FROM chunks c
                    JOIN files f ON c.file_id = f.id
                    WHERE c.id = %s;
                    """, (chunk_id,))

                    result = cur.fetchone()
                    if result:
                        return {
                            "chunk_id": result[0],
                            "chunk_num": result[1],
                            "total_chunks": result[2],
                            "content": result[3],
                            "file_path": result[4]
                        }
                    return None

        except Exception as e:
            logger.error(f"获取块内容失败: {e}")
            raise

    def search_fulltext(self, query_text: str, top_k: int = 5, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """全文搜索（文件级，保持向后兼容）"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT f.file_path, f.topic, f.last_modified, 
                           COUNT(c.id) as chunk_count, MAX(c.chunk_num) as total_chunks
                    FROM files f
                    LEFT JOIN chunks c ON f.id = c.file_id
                    WHERE f.status = 'success' AND to_tsvector('english', f.file_path) @@ plainto_tsquery('english', %s)
                    """
                    params = [query_text, top_k]

                    if topic:
                        query += " AND f.topic = %s"
                        params.insert(1, topic)

                    query += " GROUP BY f.id LIMIT %s;"
                    cur.execute(query, params)
                    results = cur.fetchall()

                    return [
                        {
                            "file_path": res[0],
                            "topic": res[1],
                            "last_modified": res[2].isoformat(),
                            "chunk_count": res[3],
                            "total_chunks": res[4]
                        } for res in results
                    ]

        except Exception as e:
            logger.error(f"全文搜索失败: {e}")
            raise

    def delete_file_chunks(self, file_id: int) -> bool:
        """删除文件的所有块记录"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM chunks WHERE file_id = %s;", (file_id,))
                    conn.commit()
                    logger.info(f"已删除文件 {file_id} 的所有块记录")
                    return True
        except Exception as e:
            logger.error(f"删除文件块记录失败: {e}")
            raise