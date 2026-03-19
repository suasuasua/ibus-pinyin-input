"""
拼音转换器模块

负责将汉字转换为拼音，支持多音字处理和缓存机制。
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json
import os

# 多音字字典 - 汉字到拼音列表的映射
# 实际项目中应从 pypinyin 获取或自定义扩展
MULTI_PHRASES = {
    '长': ['chang', 'zhang'],
    '重': ['chong', 'zhong'],
    '行': ['hang', 'xing'],
    '着': ['zhe', 'zhuo', 'zhao', 'zhai', 'zha'],
    '和': ['he', 'hè', 'huó', 'huò', 'hú'],
    '乐': ['le', 'yue'],
    '了': ['le', 'liǎo'],
    '的': ['de'],
    '地': ['de', 'dì'],
    '得': ['de', 'dé', 'děi'],
    '发': ['fa', 'fā'],
    '为': ['wei', 'wèi'],
    '好': ['hao', 'hǎo'],
    '好': ['hao', 'hǎo'],
    '是': ['shi'],
    '我': ['wo'],
    '你': ['ni'],
    '他': ['ta'],
    '们': ['men'],
    '不': ['bu'],
    '的': ['de'],
    '了': ['le'],
    '在': ['zai'],
    '有': ['you'],
    '要': ['yao'],
    '人': ['ren'],
    '这': ['zhe'],
    '那': ['na'],
    '是': ['shi'],
    '做': ['zuo'],
    '来': ['lai'],
    '去': ['qu'],
    '上': ['shang'],
    '下': ['xia'],
    '中': ['zhong'],
    '国': ['guo'],
    '大': ['da'],
    '小': ['xiao'],
    '高': ['gao'],
    '低': ['di'],
    '好': ['hao'],
    '坏': ['huai'],
    '新': ['xin'],
    '旧': ['jiu'],
    '快': ['kuai'],
    '慢': ['man'],
    '多': ['duo'],
    '少': ['shao'],
    '多': ['duo'],
    '少': ['shao'],
    '明': ['ming'],
    '白': ['bai'],
    '天': ['tian'],
    '空': ['kong'],
    '地': ['di'],
    '方': ['fang'],
    '向': ['xiang'],
    '前': ['qian'],
    '后': ['hou'],
    '左': ['zuo'],
    '右': ['you'],
    '东': ['dong'],
    '南': ['nan'],
    '西': ['xi'],
    '北': ['bei'],
    '开': ['kai'],
    '关': ['guan'],
    '灯': ['deng'],
    '电': ['dian'],
    '话': ['hua'],
    '说': ['shuo'],
    '听': ['ting'],
    '看': ['kan'],
    '见': ['jian'],
    '想': ['xiang'],
    '思': ['si'],
    '念': ['nian'],
    '忆': ['yi'],
    '想': ['xiang'],
    '爱': ['ai'],
    '恨': ['hen'],
    '喜': ['xi'],
    '欢': ['huan'],
    '悲': ['bei'],
    '哀': ['ai'],
    '乐': ['le'],
    '苦': ['ku'],
    '甜': ['tian'],
    '酸': ['suan'],
    '辣': ['la'],
    '咸': ['xian'],
    '冷': ['leng'],
    '热': ['re'],
    '冰': ['bing'],
    '火': ['huo'],
    '水': ['shui'],
    '风': ['feng'],
    '雨': ['yu'],
    '雪': ['xue'],
    '雷': ['lei'],
    '电': ['dian'],
    '云': ['yun'],
    '雾': ['wu'],
    '霜': ['shuang'],
    '露': ['lu'],
    '虹': ['hong'],
    '霓': ['ni'],
    '灯': ['deng'],
    '光': ['guang'],
    '明': ['ming'],
    '暗': ['an'],
    '亮': ['liang'],
    '暗': ['an'],
    '弱': ['ruo'],
    '强': ['qiang'],
    '壮': ['zhuang'],
    '胖': ['pang'],
    '瘦': ['shou'],
    '高': ['gao'],
    '矮': ['ai'],
    '长': ['zhang'],
    '短': ['duan'],
    '宽': ['kuan'],
    '窄': ['zhai'],
    '厚': ['hou'],
    '薄': ['bo'],
    '深': ['shen'],
    '浅': ['qian'],
    '远': ['yuan'],
    '近': ['jin'],
    '早': ['zao'],
    '晚': ['wan'],
    '晨': ['chen'],
    '昏': ['hun'],
    '夜': ['ye'],
    '昼': ['zhou'],
    '昔': ['xi'],
    '今': ['jin'],
    '朝': ['zhao'],
    '夕': ['xi'],
    '朝': ['zhao'],
    '夕': ['xi'],
}


class PinyinConverter:
    """
    拼音转换器类
    
    负责将汉字转换为拼音，支持多音字处理和缓存机制。
    
    Attributes:
        cache: 拼音转换结果缓存字典
        max_cache_size: 缓存最大大小
    """
    
    def __init__(self, max_cache_size: int = 10000):
        """
        初始化拼音转换器
        
        Args:
            max_cache_size: 缓存最大大小，默认 10000
        """
        self.cache: Dict[str, List[Tuple[str, bool]]] = defaultdict(list)
        self.max_cache_size = max_cache_size
        # 初始化常用字符的拼音
        self._init_common_characters()
    
    def _init_common_characters(self):
        """初始化常用字符的拼音缓存"""
        common_chars = [
            '的', '了', '是', '我', '你', '他', '们', '不', '在', '有',
            '要', '人', '这', '那', '做', '来', '去', '上', '下', '中',
            '国', '大', '小', '高', '低', '好', '坏', '新', '旧', '快',
            '慢', '多', '少', '明', '白', '天', '空', '地', '方', '向',
            '前', '后', '左', '右', '东', '南', '西', '北', '开', '关',
            '电', '话', '说', '听', '看', '想', '思', '念', '忆', '爱',
            '恨', '喜', '欢', '悲', '哀', '苦', '甜', '酸', '辣', '咸',
            '冷', '热', '冰', '火', '水', '风', '雨', '雪', '雷', '电',
            '云', '雾', '霜', '露', '虹', '霓', '灯', '光', '明', '暗',
            '亮', '弱', '强', '壮', '胖', '瘦', '宽', '窄', '厚', '薄',
            '深', '浅', '远', '近', '早', '晚', '晨', '昏', '夜', '昼',
            '昔', '今', '朝', '夕', '弱', '强', '壮', '胖', '瘦', '高',
            '矮', '长', '短', '宽', '窄', '厚', '薄', '深', '浅', '远',
            '近', '早', '晚', '晨', '昏', '夜', '昼', '昔', '今', '朝',
            '夕',
        ]
        for char in common_chars:
            if char in MULTI_PHRASES:
                self._set_pinyin(char, MULTI_PHRASES[char])
            else:
                # 简单拼音映射（实际应从 pypinyin 获取）
                self._set_pinyin(char, [self._simple_pinyin(char)])
    
    def _simple_pinyin(self, char: str) -> str:
        """
        简单拼音映射（用于示例）
        
        Args:
            char: 单个汉字
            
        Returns:
            拼音字符串
        """
        # 这是一个简化的映射表，实际项目中应使用 pypinyin
        # 这里只返回示例，真实实现需要使用 pypinyin 库
        return 'pinyin'  # 占位符
    
    def _set_pinyin(self, char: str, pinyin_list: List[str]):
        """
        设置字符的拼音缓存
        
        Args:
            char: 汉字字符
            pinyin_list: 拼音列表
        """
        # 限制缓存大小
        if len(self.cache[char]) < self.max_cache_size:
            self.cache[char] = pinyin_list
    
    def convert(self, text: str, tone_type: str = 'none') -> List[Tuple[str, bool]]:
        """
        将文本转换为拼音
        
        Args:
            text: 输入的文本字符串
            tone_type: 拼音输出格式
                'none': 无声调（a, b, c...）
                'single': 单字母声调（a, b, c...）
                'number': 数字声调（a1, b2, c3...）
                'symbol': 符号声调（a, b, c...）
            
        Returns:
            拼音列表，每个元素为 (拼音，是否是多音字) 的元组
            
        Raises:
            ValueError: 当 tone_type 无效时
        """
        if tone_type not in ['none', 'single', 'number', 'symbol']:
            raise ValueError(f"无效的 tone_type: {tone_type}, 必须是 none/single/number/symbol")
        
        result = []
        for char in text:
            if char == ' ':
                continue  # 跳过空格
            
            if char in self.cache:
                # 使用缓存
                pinyin_list = self.cache[char]
            else:
                # 计算拼音（实际应使用 pypinyin）
                pinyin_list = self._calculate_pinyin(char, tone_type)
                # 缓存结果
                self._set_pinyin(char, pinyin_list)
            
            # 检查是否为多音字
            is_multi = len(pinyin_list) > 1
            result.extend([(p, is_multi) for p in pinyin_list])
        
        return result
    
    def _calculate_pinyin(self, char: str, tone_type: str) -> List[str]:
        """
        计算单个字符的拼音
        
        Args:
            char: 单个汉字字符
            tone_type: 拼音输出格式
            
        Returns:
            拼音列表
        """
        # 这是一个占位符实现
        # 实际项目中应使用 pypinyin 库
        if char in MULTI_PHRASES:
            # 多音字处理
            return MULTI_PHRASES[char]
        else:
            # 单音字处理
            return [self._simple_pinyin(char)]
    
    def clear_cache(self):
        """清除所有缓存"""
        self.cache.clear()
    
    def clear_specific_cache(self, char: str):
        """
        清除指定字符的缓存
        
        Args:
            char: 要清除缓存的汉字字符
        """
        if char in self.cache:
            del self.cache[char]
    
    def get_pinyin(self, char: str) -> Optional[List[str]]:
        """
        获取字符的拼音（从缓存）
        
        Args:
            char: 汉字字符
            
        Returns:
            拼音列表，如果字符不存在则返回 None
        """
        return self.cache.get(char)
    
    def is_common_character(self, char: str) -> bool:
        """
        检查字符是否常用
        
        Args:
            char: 汉字字符
            
        Returns:
            是否为常用字符
        """
        return char in self.cache


def create_converter(max_cache_size: int = 10000) -> PinyinConverter:
    """
    工厂函数创建拼音转换器
    
    Args:
        max_cache_size: 缓存最大大小
        
    Returns:
        PinyinConverter 实例
    """
    return PinyinConverter(max_cache_size)


# 测试示例
if __name__ == "__main__":
    converter = create_converter()
    test_text = "你好世界"
    print(f"转换文本：{test_text}")
    print(f"拼音结果：{converter.convert(test_text)}")
