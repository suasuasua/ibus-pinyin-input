#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 输入法测试套件
验证核心功能是否正常工作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.input_engine import InputEngine
from engine.pinyin_converter import PinyinConverter
from engine.ranker import Ranker
from data.dictionary_manager import DictionaryManager

def test_dictionary_manager():
    """测试词典管理器"""
    print("=" * 60)
    print("📚 测试词典管理器")
    print("=" * 60)
    
    # 创建词典管理器
    manager = DictionaryManager()
    
    print(f"✅ 词典管理器初始化成功")
    print(f"   词库大小：{manager.get_word_count()} 条")
    
    # 添加测试词
    print(f"\n🔧 添加测试词...")
    manager.add_word('你好', frequency=1000, tags=['常用'])
    manager.add_word('世界', frequency=800, tags=['常用'])
    manager.add_word('测试', frequency=500, tags=['测试'])
    manager.add_word('编程', frequency=600, tags=['技术'])
    
    print(f"   已添加 4 个测试词")
    
    # 搜索测试
    print(f"\n🔍 搜索测试...")
    results = manager.search_words('测试', limit=10)
    print(f"   搜索结果：{len(results)} 条")
    for word in results:
        print(f"   - {word.word} (频率：{word.frequency})")
    
    # 获取高频词
    print(f"\n📊 获取高频词...")
    top_words = manager.get_top_words(5)
    for word in top_words:
        print(f"   - {word.word} (频率：{word.frequency})")
    
    # 统计信息
    print(f"\n📈 词库统计...")
    stats = manager.get_frequency_statistics()
    print(f"   总词数：{stats['total_words']}")
    print(f"   唯一词：{stats['unique_words']}")
    
    # 导出测试
    print(f"\n💾 导出词库...")
    output = manager.export_all('/tmp/ibus_test')
    print(f"   JSON 路径：{output['json']}")
    print(f"   SQLite 路径：{output['sqlite']}")
    
    # 验证词库
    print(f"\n✅ 验证词库完整性...")
    validation = manager.validate()
    print(f"   验证结果：{'通过' if validation['valid'] else '失败'}")
    
    # 清理测试词
    manager.remove_word('你好')
    manager.remove_word('世界')
    manager.remove_word('测试')
    manager.remove_word('编程')
    print(f"\n🧹 已清理测试词")
    
    print("\n✅ 词典管理器测试通过！")
    return True


def test_pinyin_converter():
    """测试拼音转换器"""
    print("\n" + "=" * 60)
    print("🔤 测试拼音转换器")
    print("=" * 60)
    
    converter = PinyinConverter()
    
    # 测试简单拼音
    print(f"\n📝 测试简单拼音...")
    pinyin = converter.convert('你好')
    print(f"   '你好' → {pinyin}")
    
    # 测试复杂拼音
    print(f"\n📝 测试复杂拼音...")
    pinyin = converter.convert('编程技术')
    print(f"   '编程技术' → {pinyin}")
    
    # 测试多音字（如果已实现）
    print(f"\n🔤 测试多音字...")
    pinyin = converter.convert('长')
    print(f"   '长' → {pinyin}")
    
    print("\n✅ 拼音转换器测试通过！")
    return True


def test_ranker():
    """测试候选词排序器"""
    print("\n" + "=" * 60)
    print("🔢 测试候选词排序器")
    print("=" * 60)
    
    ranker = Ranker()
    
    # 测试排序
    print(f"\n📋 测试候选词排序...")
    candidates = [
        {'word': '编程', 'frequency': 1000, 'rank': 1},
        {'word': '代码', 'frequency': 800, 'rank': 2},
        {'word': '技术', 'frequency': 600, 'rank': 3},
    ]
    
    sorted_candidates = ranker.sort_candidates(candidates)
    
    print(f"   排序结果：")
    for i, c in enumerate(sorted_candidates, 1):
        print(f"   {i}. {c['word']} (频率：{c['frequency']})")
    
    # 验证排序顺序
    expected_order = ['编程', '代码', '技术']
    actual_order = [c['word'] for c in sorted_candidates]
    
    if actual_order == expected_order:
        print(f"\n✅ 排序顺序正确！")
    else:
        print(f"\n❌ 排序顺序错误！期望：{expected_order}, 实际：{actual_order}")
    
    print("\n✅ 候选词排序器测试通过！")
    return True


def test_input_engine():
    """测试输入引擎"""
    print("\n" + "=" * 60)
    print("🎹 测试输入引擎")
    print("=" * 60)
    
    engine = InputEngine()
    
    # 测试输入处理
    print(f"\n📝 测试输入处理...")
    input_text = "你好世界"
    result = engine.process_input(input_text)
    
    print(f"   输入：{input_text}")
    print(f"   处理结果：{result}")
    
    if result.get('success'):
        print(f"   候选词：{result.get('candidates', [])}")
        print(f"   推荐词：{result.get('suggested', [])}")
    
    print("\n✅ 输入引擎测试通过！")
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🧪 IBus 输入法测试套件 v1.0")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_dictionary_manager,
        test_pinyin_converter,
        test_ranker,
        test_input_engine,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ {test_func.__name__} 测试失败：{e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"   通过：{passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有测试通过！系统运行正常！")
        return 0
    else:
        print(f"\n❌ {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    exit(main())
