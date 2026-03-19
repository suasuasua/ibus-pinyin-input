"""
IBus GSettings Schema 包装模块

提供对 GSettings schema 的 Python 友好访问。
"""

import os
from typing import Any, Dict, List, Optional
from enum import Enum


# GSettings Schema 定义
SCHEMA_ID = "ibus-config-manager"
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    'settings_schema.gschema.xml'
)


class PinyinStyle(Enum):
    """拼音输入样式枚举"""
    SIMPLIFIED = 's'
    TRADITIONAL = 't'


class CandidateStyle(Enum):
    """候选词样式枚举"""
    NORMAL = 'normal'
    COMPACT = 'compact'
    WIDE = 'wide'


class AutoConvertMode(Enum):
    """自动转换模式枚举"""
    NONE = 'none'
    ENGLISH_CHINESE = 'english-chinese'
    ENGLISH_NUMBER = 'english-number'
    ALL = 'all'


class BackupFrequency(Enum):
    """备份频率枚举"""
    NEVER = 'never'
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


class CompatMode(Enum):
    """兼容性模式枚举"""
    NONE = 'none'
    X11 = 'x11'
    WAYLAND = 'wayland'


# 配置键常量
class ConfigKeys:
    """配置键常量类"""
    # 引擎配置
    ENABLED_ENGINES = 'enabled-engines'
    DEFAULT_ENGINE = 'default-engine'
    CURRENT_ENGINE = 'current-engine'
    LANGUAGE = 'language'
    
    # 拼音配置
    PINYIN_STYLE = 'pinyin-style'
    PINYIN_CANDIDATES = 'pinyin-candidates'
    PINYIN_TONE_MARK = 'pinyin-tone-mark'
    PINYIN_FRESHNESS = 'pinyin-freshness'
    
    # 候选词配置
    CANDIDATE_STYLE = 'candidate-style'
    CANDIDATE_NUM_WIDTH = 'candidate-num-width'
    CANDIDATE_POPUP_WIDTH = 'candidate-popup-width'
    CANDIDATE_POPUP_HEIGHT = 'candidate-popup-height'
    
    # 外观配置
    SHOW_TOOLBAR = 'show-toolbar'
    SHOW_CANDIDATES = 'show-candidates'
    TOOLBAR_FONT = 'toolbar-font'
    
    # 快捷键配置
    SHOW_CANDIDATES_KEY = 'show-candidates-key'
    SELECT_KEY = 'select-key'
    NEXT_KEY = 'next-key'
    
    # 历史记录配置
    HISTORY_ENABLED = 'history-enabled'
    HISTORY_MAX_SIZE = 'history-max-size'
    HISTORY_MAX_LENGTH = 'history-max-length'
    
    # 自动转换配置
    AUTO_CONVERT = 'auto-convert'
    AUTO_CONVERT_MODE = 'auto-convert-mode'
    
    # 主题配置
    THEME = 'theme'
    THEME_COLOR = 'theme-color'
    
    # 建议配置
    SHOW_SUGGESTIONS = 'show-suggestions'
    SUGGESTION_MAX = 'suggestion-max'
    
    # 预测配置
    ENABLE_PREDICT = 'enable-predict'
    PREDICTION_MAX = 'prediction-max'
    
    # 鲜输入配置
    ENABLE_FRESH = 'enable-fresh'
    FRESH_TIMEOUT = 'fresh-timeout'
    
    # 备份配置
    BACKUP_ENABLED = 'backup-enabled'
    BACKUP_PATH = 'backup-path'
    BACKUP_FREQUENCY = 'backup-frequency'
    
    # 日志配置
    LOG_ENABLED = 'log-enabled'
    LOG_LEVEL = 'log-level'
    LOG_PATH = 'log-path'
    
    # 引擎排序
    ENGINE_ORDER = 'engine-order'
    
    # 自定义词典
    CUSTOM_DICT_ENABLED = 'custom-dict-enabled'
    CUSTOM_DICT_PATH = 'custom-dict-path'
    
    # 兼容性
    COMPAT_MODE = 'compat-mode'


# 默认配置值
DEFAULT_CONFIG = {
    ConfigKeys.ENABLED_ENGINES: [],
    ConfigKeys.DEFAULT_ENGINE: 'pinyin',
    ConfigKeys.CURRENT_ENGINE: 'pinyin',
    ConfigKeys.LANGUAGE: 'zh_CN',
    ConfigKeys.PINYIN_STYLE: PinyinStyle.SIMPLIFIED.value,
    ConfigKeys.PINYIN_CANDIDATES: 6,
    ConfigKeys.PINYIN_TONE_MARK: False,
    ConfigKeys.PINYIN_FRESHNESS: False,
    ConfigKeys.CANDIDATE_STYLE: CandidateStyle.NORMAL.value,
    ConfigKeys.CANDIDATE_NUM_WIDTH: 1,
    ConfigKeys.CANDIDATE_POPUP_WIDTH: 300,
    ConfigKeys.CANDIDATE_POPUP_HEIGHT: 200,
    ConfigKeys.SHOW_TOOLBAR: True,
    ConfigKeys.SHOW_CANDIDATES: True,
    ConfigKeys.TOOLBAR_FONT: 'Sans 12',
    ConfigKeys.SHOW_CANDIDATES_KEY: '<Control>I',
    ConfigKeys.SELECT_KEY: 'Return',
    ConfigKeys.NEXT_KEY: '<Control>Space',
    ConfigKeys.HISTORY_ENABLED: True,
    ConfigKeys.HISTORY_MAX_SIZE: 100,
    ConfigKeys.HISTORY_MAX_LENGTH: 50,
    ConfigKeys.AUTO_CONVERT: False,
    ConfigKeys.AUTO_CONVERT_MODE: AutoConvertMode.NONE.value,
    ConfigKeys.THEME: 'default',
    ConfigKeys.THEME_COLOR: '#333333',
    ConfigKeys.SHOW_SUGGESTIONS: True,
    ConfigKeys.SUGGESTION_MAX: 5,
    ConfigKeys.ENABLE_PREDICT: True,
    ConfigKeys.PREDICTION_MAX: 5,
    ConfigKeys.ENABLE_FRESH: False,
    ConfigKeys.FRESH_TIMEOUT: 1800000,
    ConfigKeys.BACKUP_ENABLED: True,
    ConfigKeys.BACKUP_FREQUENCY: BackupFrequency.DAILY.value,
    ConfigKeys.LOG_ENABLED: False,
    ConfigKeys.LOG_LEVEL: LogLevel.INFO.value,
    ConfigKeys.ENGINE_ORDER: ['pinyin', 'wubi', 'english', 'handwriting'],
    ConfigKeys.CUSTOM_DICT_ENABLED: False,
    ConfigKeys.COMPAT_MODE: CompatMode.NONE.value,
}


def validate_config(key: str, value: Any) -> bool:
    """
    验证配置值
    
    Args:
        key: 配置键
        value: 配置值
        
    Returns:
        是否有效
    """
    # 引擎类型验证
    valid_engines = ['pinyin', 'wubi', 'english', 'handwriting', 'none']
    if key in [ConfigKeys.DEFAULT_ENGINE, ConfigKeys.CURRENT_ENGINE]:
        return value in valid_engines
    
    # 拼音样式验证
    if key == ConfigKeys.PINYIN_STYLE:
        return value in ['s', 't']
    
    # 候选样式验证
    if key == ConfigKeys.CANDIDATE_STYLE:
        return value in ['normal', 'compact', 'wide']
    
    # 自动转换模式验证
    if key == ConfigKeys.AUTO_CONVERT_MODE:
        return value in ['none', 'english-chinese', 'english-number', 'all']
    
    # 备份频率验证
    if key == ConfigKeys.BACKUP_FREQUENCY:
        return value in ['never', 'hourly', 'daily', 'weekly', 'monthly']
    
    # 日志级别验证
    if key == ConfigKeys.LOG_LEVEL:
        return value in ['debug', 'info', 'warning', 'error']
    
    # 兼容性模式验证
    if key == ConfigKeys.COMPAT_MODE:
        return value in ['none', 'x11', 'wayland']
    
    # 整数范围验证
    if key == ConfigKeys.PINYIN_CANDIDATES:
        return isinstance(value, int) and 1 <= value <= 10
    
    if key == ConfigKeys.CANDIDATE_NUM_WIDTH:
        return isinstance(value, int) and 1 <= value <= 3
    
    if key == ConfigKeys.HISTORY_MAX_SIZE:
        return isinstance(value, int) and 10 <= value <= 1000
    
    if key == ConfigKeys.HISTORY_MAX_LENGTH:
        return isinstance(value, int) and 10 <= value <= 500
    
    if key == ConfigKeys.CANDIDATE_POPUP_WIDTH:
        return isinstance(value, int) and 150 <= value <= 600
    
    if key == ConfigKeys.CANDIDATE_POPUP_HEIGHT:
        return isinstance(value, int) and 100 <= value <= 400
    
    if key == ConfigKeys.FRESH_TIMEOUT:
        return isinstance(value, int) and 60000 <= value <= 3600000
    
    # 布尔值验证
    if key in [
        ConfigKeys.PINYIN_TONE_MARK,
        ConfigKeys.PINYIN_FRESHNESS,
        ConfigKeys.SHOW_TOOLBAR,
        ConfigKeys.SHOW_CANDIDATES,
        ConfigKeys.HISTORY_ENABLED,
        ConfigKeys.AUTO_CONVERT,
        ConfigKeys.SHOW_SUGGESTIONS,
        ConfigKeys.ENABLE_PREDICT,
        ConfigKeys.ENABLE_FRESH,
        ConfigKeys.BACKUP_ENABLED,
        ConfigKeys.LOG_ENABLED,
        ConfigKeys.CUSTOM_DICT_ENABLED,
    ]:
        return isinstance(value, bool)
    
    # 字符串非空验证
    if isinstance(value, str) and value:
        return True
    
    return False


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        默认配置字典
    """
    import os
    config = DEFAULT_CONFIG.copy()
    
    # 设置默认路径
    home = os.path.expanduser('~')
    config[ConfigKeys.BACKUP_PATH] = os.path.join(home, '.config', 'ibus', 'backup')
    config[ConfigKeys.LOG_PATH] = os.path.join(home, '.config', 'ibus', 'config-manager.log')
    config[ConfigKeys.CUSTOM_DICT_PATH] = os.path.join(home, '.config', 'ibus', 'dictionary')
    
    return config
