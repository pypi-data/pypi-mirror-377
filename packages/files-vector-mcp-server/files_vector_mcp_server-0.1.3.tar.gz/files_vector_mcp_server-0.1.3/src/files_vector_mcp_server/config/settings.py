import os
import json
import argparse
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 初始化日志
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """应用配置管理类"""
    # OpenAI API配置
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_api_url: str = field(default_factory=lambda: os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"))
    
    # PostgreSQL连接字符串
    db_connection_string: str = field(default_factory=lambda: os.getenv("DB_CONNECTION_STRING", "postgres://postgres:postgres@localhost:5432/postgres"))
    
    # MinerU API配置
    mineru_api_key: str = field(default_factory=lambda: os.getenv("MINERU_API_KEY", ""))
    mineru_api_url: str = field(default_factory=lambda: os.getenv("MINERU_API_URL", "https://mineru.net/api/v4"))
    
    # 主题-目录映射配置（JSON格式字符串）
    watch_topics_json: str = field(default_factory=lambda: os.getenv("WATCH_TOPICS", '{"default": ["./watch_dir"]}'))
    
    # 向量化参数配置
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"))
    embedding_dim: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "1536")))
    batch_size: int = field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "5")))
    retry_attempts: int = field(default_factory=lambda: int(os.getenv("RETRY_ATTEMPTS", "3")))
    retry_delay: int = field(default_factory=lambda: int(os.getenv("RETRY_DELAY", "5")))
    max_text_length: int = field(default_factory=lambda: int(os.getenv("MAX_TEXT_LENGTH", str(8191 * 4))))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    
    # 分块参数配置（新增）
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "4000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))
    chunk_separators: str = field(default_factory=lambda: os.getenv("CHUNK_SEPARATORS", '["\\n# ", "\\n## ", "\\n### ", "\\n#### ", "\\n\\n", "\\n", " "]'))
    
    # 派生字段（将在__post_init__中初始化）
    watch_topics: Dict[str, List[str]] = field(init=False)
    all_watch_directories: List[str] = field(init=False)
    separators: List[str] = field(init=False)  # 分块分隔符列表（派生）
    
    @classmethod
    def from_cli(cls):
        """从命令行参数创建配置实例"""
        parser = argparse.ArgumentParser(description='FastMCP文件向量服务器')
        parser.add_argument('--api-key', help='OpenAI API密钥')
        parser.add_argument('--api-url', help='OpenAI API基础URL')
        parser.add_argument('--db-connection', help='PostgreSQL连接字符串')
        parser.add_argument('--watch-topics', help='监控主题JSON配置')
        parser.add_argument('--mineru-api-key', help='MinerU API密钥')
        parser.add_argument('--mineru-api-url', help='MinerU API URL')
        parser.add_argument('--chunk-size', type=int, help='文本分块大小')
        parser.add_argument('--chunk-overlap', type=int, help='分块重叠字符数')
        
        args = parser.parse_args()
        
        # 从环境变量和命令行参数构建配置字典
        config_kwargs = {}
        
        if args.api_key:
            config_kwargs['openai_api_key'] = args.api_key
        if args.api_url:
            config_kwargs['openai_api_url'] = args.api_url
        if args.db_connection:
            config_kwargs['db_connection_string'] = args.db_connection
        if args.watch_topics:
            config_kwargs['watch_topics_json'] = args.watch_topics
        if args.mineru_api_key:
            config_kwargs['mineru_api_key'] = args.mineru_api_key
        if args.mineru_api_url:
            config_kwargs['mineru_api_url'] = args.mineru_api_url
        if args.chunk_size:
            config_kwargs['chunk_size'] = args.chunk_size
        if args.chunk_overlap:
            config_kwargs['chunk_overlap'] = args.chunk_overlap
        
        # 创建配置实例
        return cls(**config_kwargs)
    
    def __post_init__(self):
        """对象初始化后处理配置解析"""
        # 解析监控主题配置
        self._parse_watch_topics()
        
        # 解析分块分隔符
        self._parse_chunk_separators()
        
        # 验证API密钥
        self._validate_api_key()
        
        # 处理监控目录
        self._process_watch_directories()
        
        # 记录配置信息
        self._log_config()
    
    def _parse_watch_topics(self):
        """解析监控主题JSON配置"""
        try:
            self.watch_topics = json.loads(self.watch_topics_json)
            
            # 验证配置格式
            if not isinstance(self.watch_topics, dict):
                raise ValueError("WATCH_TOPICS必须是JSON对象")
                
            for topic, dirs in self.watch_topics.items():
                if not isinstance(dirs, list) or not all(isinstance(d, str) for d in dirs):
                    raise ValueError(f"主题 {topic} 的目录必须是字符串列表")
                    
        except json.JSONDecodeError as e:
            logger.error(f"WATCH_TOPICS JSON解析失败: {e}")
            logger.error('请确保WATCH_TOPICS环境变量是有效的JSON字符串，例如: \'{"工作": ["./work"]}\'')
            raise
        except ValueError as e:
            logger.error(f"WATCH_TOPICS格式错误: {e}")
            raise
    
    def _parse_chunk_separators(self):
        """解析分块分隔符配置"""
        try:
            self.separators = json.loads(self.chunk_separators)
            if not isinstance(self.separators, list) or not all(isinstance(s, str) for s in self.separators):
                raise ValueError("CHUNK_SEPARATORS必须是字符串列表")
            logger.info(f"分块分隔符配置: {self.separators[:3]}...")  # 只显示前3个
        except json.JSONDecodeError as e:
            logger.error(f"CHUNK_SEPARATORS JSON解析失败: {e}")
            logger.error('请确保CHUNK_SEPARATORS是有效的JSON数组，例如: \'["\\n## ", "\\n\\n", "\\n"]\'')
            raise
        except ValueError as e:
            logger.error(f"CHUNK_SEPARATORS格式错误: {e}")
            raise
    
    def _validate_api_key(self):
        """验证API密钥是否设置"""
        if not self.openai_api_key:
            logger.error("\n" + "="*80)
            logger.error("未找到有效的OPENAI_API_KEY!")
            logger.error("请设置环境变量或通过命令行参数提供API密钥")
            logger.error("="*80)
            raise ValueError("OPENAI_API_KEY环境变量未设置")
    
    def _process_watch_directories(self):
        """处理监控目录"""
        self.all_watch_directories = []
        for topic, directories in self.watch_topics.items():
            for directory in directories:
                abs_dir = os.path.abspath(directory)
                self.all_watch_directories.append(abs_dir)
                
                # 确保目录存在
                os.makedirs(abs_dir, exist_ok=True)
    
    def _log_config(self):
        """记录配置信息"""
        logger.info(f"使用OpenAI API URL: {self.openai_api_url}")
        logger.info(f"使用嵌入模型: {self.embedding_model}")
        logger.info(f"文本分块配置: 大小={self.chunk_size}, 重叠={self.chunk_overlap}")
        logger.info(f"监控主题配置: {list(self.watch_topics.keys())}")
        logger.info(f"监控目录: {self.all_watch_directories}")