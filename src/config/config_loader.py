"""
IBus 配置加载器

负责从各种来源加载配置，支持配置文件、GSettings、环境变量等。
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

from .settings_schema import (
    ConfigKeys,
    DEFAULT_CONFIG,
    validate_config,
    get_default_config
)
from .config_manager import ConfigManager, ConfigValidationError
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio


class ConfigLoaderError(Exception):
    """配置加载错误"""
    pass


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化配置加载器
        
        Args:
            config_manager: ConfigManager 实例（可选）
        """
        self.config_manager = config_manager or ConfigManager()
        self._config: Dict[str, Any] = {}
        self._load_sources: List[str] = []
        self._init_load_sources()
    
    def _init_load_sources(self) -> None:
        """初始化加载源"""
        self._load_sources = [
            'gsettings',  # GSettings
            'config_file',  # 配置文件
            'env_vars',  # 环境变量
        ]
    
    def load(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        从指定源加载配置
        
        Args:
            sources: 加载源列表（默认使用所有源）
            
        Returns:
            合并后的配置字典
        """
        if sources is None:
            sources = self._load_sources.copy()
        
        # 重置配置
        self._config = get_default_config().copy()
        
        # 按优先级顺序加载
        for source in sources:
            try:
                if source == 'gsettings':
                    self._load_from_gsettings()
                elif source == 'config_file':
                    self._load_from_config_file()
                elif source == 'env_vars':
                    self._load_from_env_vars()
                else:
                    logger.warning(f"Unknown load source: {source}")
            except Exception as e:
                logger.error(f"Failed to load from {source}: {e}")
        
        # 保存合并后的配置
        self._config_manager.save_all()
        
        logger.info(f"Configuration loaded from: {sources}")
        return self._config
    
    def _load_from_gsettings(self) -> None:
        """从 GSettings 加载配置"""
        logger.debug("Loading from GSettings...")
        
        # 获取 GSettings 中的配置值
        settings = self.config_manager.gsettings
        if not settings:
            logger.warning("GSettings not available")
            return
        
        # 获取所有配置值
        config = self.config_manager.get_all()
        
        # 合并到本地配置
        for key, value in config.items():
            if key in self._config:
                # 使用环境变量优先级（后加载的优先级更高）
                if isinstance(value, (str, int, bool, list)):
                    self._config[key] = value
        
        logger.info(f"Loaded {len(config)} settings from GSettings")
    
    def _load_from_config_file(self) -> None:
        """从配置文件加载配置"""
        logger.debug("Loading from config file...")
        
        config_file = os.path.expanduser('~/.config/ibus/config.json')
        
        if not os.path.exists(config_file):
            logger.debug(f"Config file not found: {config_file}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # 合并配置
            for key, value in file_config.items():
                if validate_config(key, value):
                    # 配置文件的优先级高于 GSettings
                    self._config[key] = value
            
            logger.info(f"Loaded {len(file_config)} settings from config file")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    
    def _load_from_env_vars(self) -> None:
        """从环境变量加载配置"""
        logger.debug("Loading from environment variables...")
        
        env_config = {
            'IBUS_PINYIN_STYLE': ConfigKeys.PINYIN_STYLE,
            'IBUS_PINYIN_CANDIDATES': ConfigKeys.PINYIN_CANDIDATES,
            'IBUS_SHOW_TOOLBAR': ConfigKeys.SHOW_TOOLBAR,
            'IBUS_SHOW_CANDIDATES': ConfigKeys.SHOW_CANDIDATES,
            'IBUS_THEME': ConfigKeys.THEME,
            'IBUS_LANGUAGE': ConfigKeys.LANGUAGE,
            'IBUS_HISTORY_ENABLED': ConfigKeys.HISTORY_ENABLED,
            'IBUS_AUTO_CONVERT': ConfigKeys.AUTO_CONVERT,
        }
        
        for env_key, config_key in env_config.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                try:
                    # 尝试转换为适当类型
                    if config_key in [ConfigKeys.PINYIN_CANDIDATES, ConfigKeys.PINYIN_CANDIDATES]:
                        value = int(env_value)
                    elif env_key in [
                        ConfigKeys.SHOW_TOOLBAR, ConfigKeys.SHOW_CANDIDATES,
                        ConfigKeys.HISTORY_ENABLED, ConfigKeys.AUTO_CONVERT
                    ]:
                        value = env_value.lower() in ['1', 'true', 'yes']
                    else:
                        value = env_value
                    
                    if validate_config(config_key, value):
                        self._config[config_key] = value
                except ValueError:
                    logger.warning(f"Invalid value for {env_key}: {env_value}")
        
        logger.info(f"Loaded {len([k for k, v in env_config.items() if os.environ.get(k)])} settings from env vars")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if key not in self._config:
            if default is not None:
                return default
            return self.config_manager.get(key, default)
        
        return self._config[key]
    
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
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否成功
        """
        # 验证配置
        if not validate_config(key, value):
            logger.error(f"Invalid config value: {key} = {value}")
            return False
        
        # 更新本地配置
        self._config[key] = value
        
        # 更新 GSettings
        return self.config_manager.set(key, value)
    
    def set_all(self, config: Dict[str, Any]) -> bool:
        """
        批量设置配置
        
        Args:
            config: 配置字典
            
        Returns:
            是否全部成功
        """
        success = True
        for key, value in config.items():
            if not self.set(key, value):
                success = False
        
        return success
    
    def reload(self) -> None:
        """重新加载配置"""
        logger.info("Reloading configuration...")
        
        # 清除本地配置
        self._config = get_default_config().copy()
        
        # 重新加载
        self.load()
        
        logger.info("Configuration reloaded")
    
    def save(self) -> bool:
        """保存所有配置"""
        return self.config_manager.save_all()
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            所有配置的字典
        """
        return self._config.copy()
    
    def merge(self, other_config: Dict[str, Any]) -> None:
        """
        合并另一个配置
        
        Args:
            other_config: 要合并的配置
        """
        for key, value in other_config.items():
            if validate_config(key, value):
                self._config[key] = value
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要
        
        Returns:
            配置摘要（包含关键配置项）
        """
        return {
            'enabled_engines': self.get(ConfigKeys.ENABLED_ENGINES),
            'default_engine': self.get(ConfigKeys.DEFAULT_ENGINE),
            'current_engine': self.get(ConfigKeys.CURRENT_ENGINE),
            'language': self.get(ConfigKeys.LANGUAGE),
            'pinyin_style': self.get(ConfigKeys.PINYIN_STYLE),
            'pinyin_candidates': self.get(ConfigKeys.PINYIN_CANDIDATES),
            'show_toolbar': self.get(ConfigKeys.SHOW_TOOLBAR),
            'show_candidates': self.get(ConfigKeys.SHOW_CANDIDATES),
            'candidate_style': self.get(ConfigKeys.CANDIDATE_STYLE),
            'history_enabled': self.get(ConfigKeys.HISTORY_ENABLED),
            'history_max_size': self.get(ConfigKeys.HISTORY_MAX_SIZE),
            'auto_convert': self.get(ConfigKeys.AUTO_CONVERT),
            'auto_convert_mode': self.get(ConfigKeys.AUTO_CONVERT_MODE),
            'theme': self.get(ConfigKeys.THEME),
            'enable_predict': self.get(ConfigKeys.ENABLE_PREDICT),
            'enable_fresh': self.get(ConfigKeys.ENABLE_FRESH),
            'backup_enabled': self.get(ConfigKeys.BACKUP_ENABLED),
            'backup_frequency': self.get(ConfigKeys.BACKUP_FREQUENCY),
            'log_level': self.get(ConfigKeys.LOG_LEVEL),
        }
    
    def validate(self) -> Dict[str, Any]:
        """
        验证配置有效性
        
        Returns:
            验证结果（包含错误信息）
        """
        errors = []
        
        for key, value in self._config.items():
            if not validate_config(key, value):
                errors.append({
                    'key': key,
                    'value': value,
                    'error': f"Invalid configuration: {key} = {value}"
                })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config_count': len(self._config)
        }
    
    def get_load_sources(self) -> List[str]:
        """获取加载源列表"""
        return self._load_sources.copy()
    
    def set_load_sources(self, sources: List[str]) -> None:
        """
        设置加载源列表
        
        Args:
            sources: 加载源列表
        """
        self._load_sources = sources.copy()


# 全局配置加载器实例
_loader: Optional[ConfigLoader] = None


def get_config_loader(config_manager: Optional[ConfigManager] = None) -> ConfigLoader:
    """
    获取全局配置加载器实例
    
    Args:
        config_manager: ConfigManager 实例（可选）
        
    Returns:
        ConfigLoader 实例
    """
    global _loader
    if _loader is None:
        _loader = ConfigLoader(config_manager)
    return _loader


def init_config_loader(config_manager: Optional[ConfigManager] = None) -> ConfigLoader:
    """初始化配置加载器"""
    return get_config_loader(config_manager)
