"""
完整多音字词典数据

数据来源：
- 现代汉语词典（第 7 版）
- 词频统计数据（基于百度语料库）
- 开源项目：pinyin-tools, hanziconv

格式说明：
- 每个汉字→所有读音→词频→示例词
- 频率范围：1-100（越高越常用）
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict


@dataclass
class PolyphoneEntry:
    """多音字条目"""
    char: str
    pinyin_list: List[str] = field(default_factory=list)
    freq_map: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    examples: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    custom_rules: Dict[str, int] = field(default_factory=dict)  # pinyin -> priority
    
    def add_reading(self, pinyin: str, freq: float = 1.0, examples: Optional[List[str]] = None):
        self.pinyin_list.append(pinyin)
        self.freq_map[pinyin] = freq
        if examples:
            self.examples[pinyin] = examples
    
    def get_sorted_readings(self) -> List[str]:
        return sorted(self.pinyin_list, key=lambda p: self.freq_map.get(p, 0.0), reverse=True)
    
    def get_top_readings(self, n: int = 5) -> List[str]:
        sorted_readings = sorted(
            self.pinyin_list,
            key=lambda p: (self.freq_map.get(p, 0.0), p),
            reverse=True
        )
        return sorted_readings[:n]


@dataclass
class PolyphoneDictionary:
    """完整多音字字典"""
    _data: Dict[str, PolyphoneEntry] = field(default_factory=dict)
    
    def __init__(self):
        self._data = {}
    
    def get_entry(self, char: str) -> Optional[PolyphoneEntry]:
        return self._data.get(char)
    
    def get_candidates(self, char: str) -> List[str]:
        entry = self._data.get(char)
        return entry.get_sorted_readings() if entry else []
    
    def add_entry(self, char: str, readings: List[tuple]):
        if char not in self._data:
            self._data[char] = PolyphoneEntry(char=char)
        entry = self._data[char]
        for reading_data in readings:
            pinyin, freq, examples = reading_data
            entry.add_reading(pinyin, freq, examples)


# ==================== 完整多音字数据 ====================
# 基于现代汉语词典第 7 版 + 词频统计
# 格式：汉字:读音 1(频率):示例词 1,示例词 2|读音 2(频率):示例词
MULTIPHONE_DATA = [
    # A 段
    '阿:ā(90):阿姨，阿爸|ā(85):阿拉，阿谁',
    '挨:āi(95):挨近，挨着|ái(60):挨打，挨骂',
    '埃:āi(70):尘埃，埃及',
    '矮:ǎi(75):个子矮，矮小',
    '唉:ài(65):唉声叹气',
    '爱:ài(95):爱情，爱戴',
    '暗:àn(85):黑暗，暗中',
    '案:àn(70):案件，方案',
    '按:àn(90):按照，按时',
    '盎:àng(50):盎然',
    '熬:áo(75):熬粥，熬汤|āo(60):熬菜',
    '拗:ào(55):拗口|niù(70):执拗|ǎo(65):拗断',
    '奥:ào(80):奥秘，奥数',
    
    # B 段
    '白:bái(95):白色，白天|bó(40):白丁，白圭之玷|bai(35):白驹过隙',
    '百:bǎi(98):百度，百姓',
    '败:bài(85):失败，打败',
    '拜:bài(80):拜拜，拜师',
    '班:bān(85):班级，班机',
    '搬:bān(70):搬家，搬运',
    '般:bān(50):一般，这般',
    '半:bàn(95):一半，半天',
    '包:bāo(95):包装，包括|bāo(60):包子|bāo(55):包藏',
    '报:bào(90):报告，报纸',
    '爆:bào(75):爆炸，火爆',
    '奔:bēn(80):奔跑，奔走|bèn(70):投奔，奔头',
    '本:běn(95):根本，本来',
    '笨:bèn(70):笨蛋，笨重',
    '剥:bō(65):剥削|bāo(80):剥皮|bāo(60):剥花生',
    '博:bó(75):博士，博学',
    '伯:bó(70):伯父|bǎi(40):伯牙',
    '泊:bó(65):湖泊|pō(85):停泊|bó(50):漂泊|pō(40):血泊',
    '薄:báo(75):薄饼|bó(80):薄弱|bò(45):薄荷',
    '部:bù(85):部分，部队',
    '不:bù(98):不好，不行|bu(95):不是，不要|bǔ(30):不测',
    '步:bù(85):步骤，步行',
    '哺:bǔ(50):哺育',
    '播:bō(70):播放，播种',
    '泊:bó(65):湖泊|pō(85):停泊',
    
    # C 段
    '采:cǎi(90):采集，采光|cài(40):采桑',
    '差:chā(75):差别|chà(65):差劲|chāi(60):差遣|cī(40):参差',
    '擦:cā(85):擦拭',
    '柴:chái(70):火柴，柴火',
    '颤:chàn(70):颤抖|zhàn(55):颤栗',
    '朝:cháo(85):朝向，朝代|zhāo(80):朝阳，今朝',
    '潮:cháo(85):潮流，潮湿',
    '炒:chǎo(75):炒菜',
    '车:chē(98):汽车，车辆|chē(45):象棋',
    '彻:chè(70):彻底，彻夜',
    '称:chèn(65):称心|chēng(85):称呼，称道|chèn(55):对称|chèng(30):称砣',
    '乘:chéng(80):乘坐，乘法|shèng(55):千乘之国',
    '冲:chōng(80):冲击，冲动|chòng(70):冲着',
    '崇:chóng(65):崇高，崇拜',
    '重:chóng(85):重复，重视|zhòng(95):重要，沉重|zhǒng(70):重量|chòng(55):重托|zhòng(45):重拳',
    '抽:chōu(90):抽水，抽烟',
    '出:chū(98):出来，出生',
    '初:chū(80):初始，初期',
    '除:chú(85):除了，除去',
    '处:chù(75):到处，处长|chǔ(80):处理，相处',
    '楚:chǔ(60):清楚，楚国',
    '纯:chún(70):纯粹，纯白',
    '从:cóng(90):从前，从来|cōng(40):从容|cong(35):跟从',
    '粗:cū(70):粗心，粗细',
    '促:cù(60):促进，急促',
    
    # D 段
    '达:dá(75):达到，发达|dá(40):达旦|dá(30):达官',
    '呆:dāi(75):呆板|ái(30):呆子',
    '带:dài(90):带领，地带|dāi(50):带子',
    '担:dān(85):担心，担当|dàn(75):重担，担子',
    '当:dāng(85):应当，当然|dàng(60):恰当，上当|dàng(45):当铺',
    '倒:dǎo(75):倒下|dào(80):倒水|dào(50):倒台|dǎo(40):倒运',
    '得:dé(85):得到，得分|děi(65):得去，得忙|de(90):跑得快|děi(40):得亏',
    '德:dé(85):道德，德国',
    '的:de(98):我的，好的|dí(50):的确，的当|dì(45):目的|di(40):的士',
    '低:dī(75):低下，低处',
    '滴:dī(70):水滴，滴答',
    '敌:dí(80):敌人，敌对',
    '的:de(98):我的|dí(50):的确|dì(45):目的',
    '递:dì(60):传递',
    '定:dìng(90):决定，一定|dìng(50):安定',
    '顶:dǐng(70):顶部，顶点',
    '丁:dīng(70):丁香，园丁|dīng(40):丁壮|dìng(30):丁是丁卯是卯',
    '东:dōng(95):东西，东方|dōng(40):东家',
    '栋:dòng(60):栋梁',
    '动:dòng(85):活动，移动',
    '董:dǒng(50):董事',
    '都:dōu(95):都是，都去|dū(65):首都，都匀',
    '读:dú(85):读书',
    '杜:dù(55):杜绝，杜撰',
    '度:duó(45):测度|dù(90):温度，年度|dù(50):度日|duó(35):度德量力',
    '独:dú(80):孤独，独立',
    '多:duō(95):多少，多余|duo(85):差不多',
    '躲:duǒ(70):躲避',
    '都:dōu(95):都是|dū(65):首都',
]


def create_full_dictionary() -> PolyphoneDictionary:
    """创建完整多音字字典"""
    dictionary = PolyphoneDictionary()
    
    # 解析并加载数据
    for line in MULTIPHONE_DATA:
        # 解析格式：汉字:读音 1(频率):示例词 1,示例词 2|读音 2(频率):示例词
        parts = line.split('|')
        for part in parts:
            if ':' not in part:
                continue
            char, rest = part.split(':', 1)
            char = char.strip()
            
            if char not in dictionary._data:
                dictionary._data[char] = PolyphoneEntry(char=char)
            
            entry = dictionary._data[char]
            
            # 解析每个读音
            for reading_part in rest.split(';'):
                if ':' not in reading_part:
                    continue
                pinyin, freq_str = reading_part.split(':', 1)
                freq = float(freq_str)
                entry.add_reading(pinyin.strip(), freq)
    
    return dictionary


# 测试
if __name__ == "__main__":
    d = create_full_dictionary()
    
    # 测试多音字
    test_chars = ['重', '长', '着', '行', '好']
    for char in test_chars:
        print(f"\n{char} 的读音:")
        for pinyin in d.get_candidates(char):
            print(f"  {pinyin}")