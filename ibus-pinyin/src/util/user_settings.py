"""
用户自定义多音字读音模块

支持用户自定义多音字读音：
- 设置优先读音
- 添加个人词库
- 保存用户偏好
- 持久化存储
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class CustomPinyinRule:
    """用户自定义读音规则"""
    char: str  # 汉字
    pinyin: str  # 自定义读音
    priority: int = 100  # 优先级（越大越优先）
    created_at: str = ""
    updated_at: str = ""
    is_global: bool = False  # 是否全局生效
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'char': self.char,
            'pinyin': self.pinyin,
            'priority': self.priority,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_global': self.is_global,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CustomPinyinRule':
        """从字典创建"""
        return cls(
            char=data['char'],
            pinyin=data['pinyin'],
            priority=data.get('priority', 100),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            is_global=data.get('is_global', False),
        )


@dataclass
class UserPolyphoneConfig:
    """用户多音字配置"""
    custom_rules: Dict[str, CustomPinyinRule] = field(default_factory=dict)
    personal_dict: Dict[str, List[str]] = field(default_factory=dict)  # 个人词库
    preferences: Dict[str, str] = field(default_factory=dict)  # 用户偏好
    
    def __init__(self):
        self.custom_rules = {}
        self.personal_dict = {}
        self.preferences = {}
    
    def add_custom_rule(self, char: str, pinyin: str, priority: int = 100, is_global: bool = False):
        """添加自定义读音规则"""
        rule = CustomPinyinRule(
            char=char,
            pinyin=pinyin,
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            is_global=is_global,
        )
        
        self.custom_rules[char] = rule
        self.preferences[char] = pinyin
    
        if is_global:
            # 全局规则优先级最高
            rule.priority = 1000
    
    def get_custom_pinyin(self, char: str) -> Optional[str]:
        """获取自定义读音"""
        if char in self.custom_rules:
            return self.custom_rules[char].pinyin
        return None
    
    def get_custom_rule(self, char: str) -> Optional[CustomPinyinRule]:
        """获取自定义规则"""
        return self.custom_rules.get(char)
    
    def set_priority(self, char: str, priority: int):
        """设置优先级"""
        if char in self.custom_rules:
            self.custom_rules[char].priority = priority
            self.custom_rules[char].updated_at = datetime.now().isoformat()
    
    def remove_rule(self, char: str):
        """移除规则"""
        if char in self.custom_rules:
            del self.custom_rules[char]
            if char in self.preferences:
                del self.preferences[char]
    
    def add_to_personal_dict(self, word: str, pinyin: str):
        """添加到个人词库"""
        if word not in self.personal_dict:
            self.personal_dict[word] = []
        if pinyin not in self.personal_dict[word]:
            self.personal_dict[word].append(pinyin)
    
    def get_personal_dict(self, char: str) -> List[str]:
        """获取包含该字的个人词库读音"""
        words = []
        for word, py_list in self.personal_dict.items():
            if char in word:
                words.extend(py_list)
        return list(set(words))  # 去重
    
    def save(self, file_path: str):
        """保存到文件"""
        data = {
            'version': '1.0',
            'custom_rules': {k: v.to_dict() for k, v in self.custom_rules.items()},
            'personal_dict': self.personal_dict,
            'preferences': self.preferences,
            'last_updated': datetime.now().isoformat(),
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, file_path: str) -> 'UserPolyphoneConfig':
        """从文件加载"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls()
            
            # 加载自定义规则
            for char, rule_data in data.get('custom_rules', {}).items():
                config.custom_rules[char] = CustomPinyinRule.from_dict(rule_data)
            
            # 加载个人词库
            config.personal_dict = data.get('personal_dict', {})
            
            # 加载偏好
            config.preferences = data.get('preferences', {})
            
            return config
        except FileNotFoundError:
            return cls()
        except json.JSONDecodeError:
            return cls()


class UserPolyphoneManager:
    """用户多音字管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = UserPolyphoneConfig()
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置路径"""
        home = Path.home()
        return str(home / ".config" / "ibus-pinyin" / "user_polyphone.json")
    
    def _load_config(self):
        """加载配置"""
        if os.path.exists(self.config_path):
            self.config = UserPolyphoneConfig.load(self.config_path)
    
    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.config.save(self.config_path)
    
    def add_custom_pinyin(self, char: str, pinyin: str, 
                         is_global: bool = False):
        """添加自定义读音"""
        self.config.add_custom_rule(char, pinyin, is_global=is_global)
        self.save_config()
    
    def set_priority(self, char: str, priority: int):
        """设置读音优先级"""
        self.config.set_priority(char, priority)
        self.save_config()
    
    def get_custom_pinyin(self, char: str) -> Optional[str]:
        """获取自定义读音"""
        return self.config.get_custom_pinyin(char)
    
    def remove_custom_pinyin(self, char: str):
        """移除自定义读音"""
        self.config.remove_rule(char)
        self.save_config()
    
    def add_to_personal_dict(self, word: str, pinyin: str):
        """添加到个人词库"""
        self.config.add_to_personal_dict(word, pinyin)
        self.save_config()
    
    def get_personal_dict(self, char: str) -> List[str]:
        """获取个人词库中的读音"""
        return self.config.get_personal_dict(char)
    
    def list_all_custom_rules(self) -> Dict[str, str]:
        """列出所有自定义规则"""
        return {k: v.pinyin for k, v in self.config.custom_rules.items()}
    
    def get_preferences(self) -> Dict[str, str]:
        """获取用户偏好"""
        return self.config.preferences
    
    def clear_all(self):
        """清空所有自定义规则"""
        self.config = UserPolyphoneConfig()
        self.save_config()
    
    def export_rules(self, file_path: str):
        """导出所有规则到文件"""
        data = {
            'char': v.char,
            'pinyin': v.pinyin,
            'priority': v.priority,
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def apply_user_rules(polyphone_dict: 'util.polyphone.PolyphoneDictionary',
                    user_manager: UserPolyphoneManager) -> 'util.polyphone.PolyphoneDictionary':
    """
    应用用户自定义规则到多音字字典
    
    Args:
        polyphone_dict: 原始多音字字典
        user_manager: 用户管理器
        
    Returns:
        更新后的多音字字典
    """
    for char, pinyin in user_manager.get_preferences().items():
        if char in polyphone_dict:
            entry = polyphone_dict.get_entry(char)
            if entry:
                # 更新优先级
                entry.set_custom_rule(pinyin, 1000)
                # 添加示例词
                entry.examples[pinyin] = user_manager.get_personal_dict(char)
    
    return polyphone_dict


def create_user_manager(config_path: str = None) -> UserPolyphoneManager:
    """创建用户管理器实例"""
    return UserPolyphoneManager(config_path)


if __name__ == "__main__":
    # 测试
    manager = UserPolyphoneManager()
    
    # 添加自定义读音
    manager.add_custom_pinyin('重', 'zhòng', is_global=True)
    manager.add_custom_pinyin('长', 'cháng')
    manager.add_custom_pinyin('好', 'hǎo')
    
    # 添加到个人词库
    manager.add_to_personal_dict('重要', 'zhòng')
    manager.add_to_personal_dict('成长', 'cháng')
    
    # 获取自定义读音
    print("自定义读音:")
    for char, pinyin in manager.list_all_custom_rules().items():
        print(f"  {char}: {pinyin}")
    
    # 保存配置
    manager.save_config()
    
    # 加载配置
    manager2 = UserPolyphoneManager()
    print("\n加载后的自定义读音:")
    for char, pinyin in manager2.list_all_custom_rules().items():
        print(f"  {char}: {pinyin}")
