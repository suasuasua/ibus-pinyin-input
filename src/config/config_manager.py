"""
IBus 中文输入法配置管理器

提供 GSettings 集成、配置加载/保存、热加载等核心功能。
"""

import os
import json
import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

# 导入 GSettings schema
from .settings_schema import SCHEMA_PATH

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ibus-config-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ibus-config-manager')


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigManager:
    """IBus 配置管理器"""
    
    def __init__(self, schema_id: str = 'ibus-config-manager'):
        """
        初始化配置管理器
        
        Args:
            schema_id: GSettings schema ID
        """
        self.schema_id = schema_id
        self.gsettings: Optional[Gio.Settings] = None
        self._load_settings()
        self._init_default_config()
        self._config_changed_handlers: List[callable] = []
        
        logger.info(f"ConfigManager initialized with schema: {schema_id}")
    
    def _load_settings(self) -> None:
        """加载 GSettings"""
        try:
            # 动态导入 GSettings schema
            import sys
            import importlib.util
            
            # 尝试加载 schema
            schema_path = os.path.join(
                os.path.dirname(__file__),
                'settings_schema.gschema.xml'
            )
            
            if os.path.exists(schema_path):
                # 注册 schema 到 GSettings
                settings = Gio.Settings.new_with_path(
                    self.schema_id,
                    '/ibus/config-manager/'
                )
                self.gsettings = settings
                logger.info("GSettings loaded successfully")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
                # 如果没有 schema 文件，使用内存设置
                self.gsettings = Gio.Settings.new_in_memory(self.schema_id)
        except Exception as e:
            logger.error(f"Failed to load GSettings: {e}")
            raise
    
    def _init_default_config(self) -> None:
        """初始化默认配置"""
        default_config = {
            'enabled-engines': [],
            'default-engine': 'pinyin',
            'pinyin-style': 's',
            'pinyin-candidates': 6,
            'pinyin-tone-mark': False,
            'pinyin-freshness': False,
            'candidate-style': 'normal',
            'candidate-num-width': 1,
            'show-toolbar': True,
            'show-candidates': True,
            'candidate-popup-width': 300,
            'candidate-popup-height': 200,
            'toolbar-font': 'Sans 12',
            'show-candidates-key': '<Control>I',
            'select-key': 'Return',
            'next-key': '<Control>Space',
            'current-engine': 'pinyin',
            'language': 'zh_CN',
            'history-enabled': True,
            'history-max-size': 100,
            'history-max-length': 50,
            'auto-convert': False,
            'auto-convert-mode': 'none',
            'theme': 'default',
            'theme-color': '#333333',
            'show-suggestions': True,
            'suggestion-max': 5,
            'enable-predict': True,
            'prediction-max': 5,
            'enable-fresh': False,
            'fresh-timeout': 1800000,
            'backup-enabled': True,
            'backup-path': os.path.expanduser('~/.config/ibus/backup'),
            'backup-frequency': 'daily',
            'log-enabled': False,
            'log-level': 'info',
            'log-path': os.path.expanduser('~/.config/ibus/config-manager.log'),
            'engine-order': ['pinyin', 'wubi', 'english', 'handwriting'],
            'custom-dict-enabled': False,
            'custom-dict-path': os.path.expanduser('~/.config/ibus/dictionary'),
            'compat-mode': 'none',
        }
        
        # 设置默认值
        for key, value in default_config.items():
            if not self.gsettings.has_key(key):
                self.gsettings.set(key, value)
                logger.debug(f"Set default value for {key}: {value}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if self.gsettings is None:
            return default
        
        try:
            value = self.gsettings.get(key)
            logger.debug(f"Get config: {key} = {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值"""
        value = self.get(key, default)
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置值"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        return default
    
    def get_str(self, key: str, default: str = '') -> str:
        """获取字符串配置值"""
        value = self.get(key, default)
        if isinstance(value, str):
            return value
        return str(value)
    
    def get_list(self, key: str, default: List = None) -> List:
        """获取列表配置值"""
        value = self.get(key, default)
        if isinstance(value, list):
            return value
        return default or []
    
    def get_dict(self, key: str, default: Dict = None) -> Dict:
        """获取字典配置值"""
        value = self.get(key, default)
        if isinstance(value, dict):
            return value
        return default or {}
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
            
        Returns:
            是否成功
        """
        if self.gsettings is None:
            logger.error("GSettings not initialized")
            return False
        
        # 验证类型
        if not self._validate_type(key, value):
            logger.error(f"Invalid type for {key}: {value}")
            return False
        
        try:
            self.gsettings.set(key, value)
            self._on_config_changed(key)
            logger.debug(f"Set config: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    def _validate_type(self, key: str, value: Any) -> bool:
        """
        验证配置值类型
        
        Args:
            key: 配置键名
            value: 配置值
            
        Returns:
            是否类型正确
        """
        # 这里应该根据 schema 定义进行更严格的验证
        # 简化版：只检查基本类型
        basic_types = (str, int, bool, list, dict)
        return isinstance(value, basic_types)
    
    def _on_config_changed(self, key: str) -> None:
        """
        配置变更通知
        
        Args:
            key: 变更的配置键
        """
        for handler in self._config_changed_handlers:
            try:
                handler(key, self.get(key))
            except Exception as e:
                logger.error(f"Config changed handler error: {e}")
    
    def connect_changed(self, handler: callable) -> None:
        """
        连接配置变更信号
        
        Args:
            handler: 回调函数，签名：handler(key: str, value: Any)
        """
        self._config_changed_handlers.append(handler)
    
    def disconnect_changed(self, handler: callable) -> None:
        """
        断开配置变更信号
        
        Args:
            handler: 要移除的回调函数
        """
        if handler in self._config_changed_handlers:
            self._config_changed_handlers.remove(handler)
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置值
        
        Returns:
            所有配置的字典
        """
        config = {}
        
        # 获取 GSettings 中所有键
        settings = self.gsettings
        if settings:
            # 遍历常用配置键
            all_keys = [
                'enabled-engines', 'default-engine', 'pinyin-style',
                'pinyin-candidates', 'pinyin-tone-mark', 'pinyin-freshness',
                'candidate-style', 'candidate-num-width', 'show-toolbar',
                'show-candidates', 'candidate-popup-width', 'candidate-popup-height',
                'toolbar-font', 'show-candidates-key', 'select-key', 'next-key',
                'current-engine', 'language', 'history-enabled', 'history-max-size',
                'history-max-length', 'auto-convert', 'auto-convert-mode',
                'theme', 'theme-color', 'show-suggestions', 'suggestion-max',
                'enable-predict', 'prediction-max', 'enable-fresh', 'fresh-timeout',
                'backup-enabled', 'backup-path', 'backup-frequency',
                'log-enabled', 'log-level', 'log-path', 'engine-order',
                'custom-dict-enabled', 'custom-dict-path', 'compat-mode'
            ]
            
            for key in all_keys:
                config[key] = settings.get(key)
        
        return config
    
    def save_all(self) -> bool:
        """
        保存所有配置
        
        Returns:
            是否成功
        """
        try:
            config = self.get_all()
            # 这里可以将配置持久化到文件
            self._persist_config(config)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def _persist_config(self, config: Dict[str, Any]) -> None:
        """
        持久化配置到文件
        
        Args:
            config: 配置字典
        """
        try:
            config_path = os.path.expanduser('~/.config/ibus/config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"Config persisted to {config_path}")
        except Exception as e:
            logger.error(f"Failed to persist config: {e}")
    
    def reload(self) -> None:
        """
        热加载配置
        
        重新从 GSettings 读取最新配置
        """
        logger.info("Reloading configuration...")
        # 重新获取所有配置值
        config = self.get_all()
        
        # 触发配置变更通知
        for key, value in config.items():
            self._on_config_changed(key)
        
        logger.info("Configuration reloaded successfully")
    
    def clear(self) -> None:
        """清除配置"""
        try:
            self.gsettings.reset()
            logger.info("Configuration cleared")
        except Exception as e:
            logger.error(f"Failed to clear config: {e}")
    
    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            是否成功
        """
        try:
            self._init_default_config()
            self.save_all()
            self.reload()
            logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False
    
    @property
    def current_engine(self) -> str:
        """获取当前激活的引擎"""
        return self.get_str('current-engine', 'pinyin')
    
    @current_engine.setter
    def current_engine(self, value: str) -> None:
        """设置当前激活的引擎"""
        self.set('current-engine', value)
    
    @property
    def language(self) -> str:
        """获取输入语言"""
        return self.get_str('language', 'zh_CN')
    
    @language.setter
    def language(self, value: str) -> None:
        """设置输入语言"""
        self.set('language', value)
    
    @property
    def enabled_engines(self) -> List[str]:
        """获取已启用的引擎列表"""
        return self.get_list('enabled-engines', ['pinyin'])
    
    @enabled_engines.setter
    def enabled_engines(self, value: List[str]) -> None:
        """设置已启用的引擎列表"""
        self.set('enabled-engines', value)
    
    @property
    def default_engine(self) -> str:
        """获取默认引擎"""
        return self.get_str('default-engine', 'pinyin')
    
    @default_engine.setter
    def default_engine(self, value: str) -> None:
        """设置默认引擎"""
        self.set('default-engine', value)


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        ConfigManager 实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def init_config_manager() -> ConfigManager:
    """
    初始化配置管理器
    
    Returns:
        ConfigManager 实例
    """
    return get_config_manager()
