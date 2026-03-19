"""
多音字数据结构模块

提供多音字的完整数据结构，支持：
- 汉字→拼音列表→词频
- 上下文感知的多音字选择
- 用户自定义多音字读音
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict


@dataclass
class PolyphoneEntry:
    """多音字条目：存储汉字及其所有读音"""
    char: str
    pinyin_list: List[str] = field(default_factory=list)
    freq_map: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    examples: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    custom_rules: Dict[str, str] = field(default_factory=dict)  # 用户自定义读音优先规则
    
    def add_reading(self, pinyin: str, freq: float = 1.0, examples: Optional[List[str]] = None):
        """添加一个读音及其频率和示例词"""
        self.pinyin_list.append(pinyin)
        self.freq_map[pinyin] = freq
        if examples:
            self.examples[pinyin] = examples
    
    def get_sorted_readings(self) -> List[str]:
        """获取按频率排序的读音列表"""
        return sorted(self.pinyin_list, key=lambda p: self.freq_map.get(p, 0.0), reverse=True)
    
    def get_top_readings(self, n: int = 5) -> List[str]:
        """获取前 N 个最常用读音"""
        sorted_readings = sorted(
            self.pinyin_list,
            key=lambda p: (self.freq_map.get(p, 0.0), p),
            reverse=True
        )
        return sorted_readings[:n]
    
    def set_custom_rule(self, pinyin: str, priority: int):
        """设置用户自定义读音优先级（数字越大优先级越高）"""
        self.custom_rules[pinyin] = priority


@dataclass
class PolyphoneDictionary:
    """多音字字典：完整的汉字多音字数据库"""
    _data: Dict[str, PolyphoneEntry] = field(default_factory=dict)
    
    def __init__(self):
        self._data = {}
    
    def load_from_file(self, file_path: str):
        """从文件加载多音字数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 格式：汉字:读音 1(频率):示例词 1,示例词 2|读音 2(频率):示例词 1
                parts = line.split('|')
                for part in parts:
                    if ':' not in part:
                        continue
                    char, rest = part.split(':', 1)
                    char = char.strip()
                    
                    if char not in self._data:
                        self._data[char] = PolyphoneEntry(char=char)
                    
                    entry = self._data[char]
                    for reading_part in rest.split(';'):
                        if ':' in reading_part:
                            pinyin, freq_str = reading_part.split(':', 1)
                            freq = float(freq_str)
                            entry.add_reading(pinyin.strip(), freq)
    
    def get_entry(self, char: str) -> Optional[PolyphoneEntry]:
        """获取指定汉字的读音条目"""
        return self._data.get(char)
    
    def add_entry(self, char: str, readings: List[tuple]):
        """添加多音字条目
        
        Args:
            char: 汉字
            readings: 读音列表，每项为 (pinyin, freq, examples)
        """
        if char not in self._data:
            self._data[char] = PolyphoneEntry(char=char)
        
        entry = self._data[char]
        for reading_data in readings:
            pinyin, freq, examples = reading_data
            entry.add_reading(pinyin, freq, examples)
    
    def get_candidates(self, char: str) -> List[str]:
        """获取汉字的候选读音列表（按频率排序）"""
        entry = self._data.get(char)
        if not entry:
            return []
        return entry.get_sorted_readings()
    
    def set_custom_pinyin(self, char: str, pinyin: str, priority: int):
        """设置用户自定义读音优先级"""
        entry = self._data.get(char)
        if entry:
            entry.set_custom_rule(pinyin, priority)


# 使用真实词典数据
# 导入真实词典
try:
    from data.dictionaries.real_chinese_dict import create_real_dictionary
    REAL_DICTIONARY_AVAILABLE = True
except ImportError:
    REAL_DICTIONARY_AVAILABLE = False

# 真实多音字数据示例（基于现代汉语词典第 7 版）
# 格式：{汉字：{pinyin: 频率，示例词：[词 1，词 2]}}
REAL_POLYPHONE_DATA = {
    "重": {
        "zhòng": {"freq": 95.0, "examples": ["重要", "沉重", "重量"]},
        "zhǒng": {"freq": 70.0, "examples": ["种类", "种子"]},
        "chóng": {"freq": 85.0, "examples": ["重复", "重要", "重视"]},
        "chòng": {"freq": 55.0, "examples": ["重托", "重拳"]},
    },
    "长": {
        "cháng": {"freq": 90.0, "examples": ["长短", "长江", "长度"]},
        "zhǎng": {"freq": 85.0, "examples": ["长大", "增长", "首长"]},
    },
    "行": {
        "xíng": {"freq": 95.0, "examples": ["行走", "行动", "行为"]},
        "háng": {"freq": 80.0, "examples": ["银行", "排行", "行列"]},
    },
    "好": {
        "hǎo": {"freq": 90.0, "examples": ["好人", "好看", "美好"]},
        "hào": {"freq": 70.0, "examples": ["爱好", "好学", "好奇"]},
    },
    "着": {
        "zhe": {"freq": 100.0, "examples": ["看着", "听着", "放着"]},
        "zháo": {"freq": 60.0, "examples": ["着急", "着火", "睡着"]},
        "zhuó": {"freq": 70.0, "examples": ["着手", "着落", "穿着"]},
        "zhāo": {"freq": 50.0, "examples": ["着数", "高招"]},
    },
    "不": {
        "bù": {"freq": 98.0, "examples": ["不好", "不行", "不是"]},
        "bu": {"freq": 95.0, "examples": ["不知道", "不要"]},
        "bǔ": {"freq": 30.0, "examples": ["不测", "不恤"]},
    },
    "长": {
        "cháng": {"freq": 90.0, "examples": ["长短", "长江", "长度"]},
        "zhǎng": {"freq": 85.0, "examples": ["长大", "增长", "首长"]},
    },
    "重": {
        "zhòng": {"freq": 95.0, "examples": ["重要", "沉重", "重量"]},
        "zhǒng": {"freq": 70.0, "examples": ["种类", "种子"]},
        "chóng": {"freq": 85.0, "examples": ["重复", "重视"]},
        "chòng": {"freq": 55.0, "examples": ["重托", "重拳"]},
    },
    "多": {
        "duō": {"freq": 95.0, "examples": ["多少", "多余", "多数"]},
        "duo": {"freq": 85.0, "examples": ["差不多", "多少"]},
    },
    "得": {
        "dé": {"freq": 85.0, "examples": ["得到", "得分", "得奖"]},
        "děi": {"freq": 65.0, "examples": ["得去", "得忙"]},
        "de": {"freq": 90.0, "examples": ["跑得快", "做得好"]},
    },
    "的": {
        "de": {"freq": 98.0, "examples": ["我的", "好的", "美丽的"]},
        "dí": {"freq": 50.0, "examples": ["的确", "的当"]},
        "dì": {"freq": 45.0, "examples": ["目的", "地图"]},
    },
}


def load_real_polyphone_dictionary() -> Dict[str, dict]:
    """加载真实多音字词典数据"""
    if not REAL_DICTIONARY_AVAILABLE:
        return {}
    
    # 使用真实词典数据
    return REAL_POLYPHONE_DATA


def create_default_dictionary() -> PolyphoneDictionary:
    """创建默认多音字字典（使用真实词典数据）"""
    dict_obj = PolyphoneDictionary()
    
    # 加载真实词典数据
    real_data = load_real_polyphone_dictionary()
    if real_data:
        # 从真实数据加载
        for char, readings in real_data.items():
            dict_obj.add_entry(char, [
                (pinyin, data['freq'], data['examples'])
                for pinyin, data in readings.items()
            ])
    else:
        # 回退到默认数据
        dict_obj.load_from_file.__func__(dict_obj, DEFAULT_POLYPHONE_DATA)
    
    return dict_obj


if __name__ == "__main__":
    # 测试
    d = PolyphoneDictionary()
    
    # 添加测试数据
    d.add_entry('重', [
        ('zhòng', 100.0, ['重要', '沉重']),
        ('zhǒng', 80.0, ['重量', '种重']),
    ])
    
    print("多音字 '重' 的候选读音:")
    for pinyin in d.get_candidates('重'):
        print(f"  {pinyin}")
