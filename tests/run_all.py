"""
运行所有测试 — 串联 test_linkages, test_geo, test_security

用法:
  python tests/run_all.py
  python tests/run_all.py -v          # 详细模式
  python -m tests.run_all            # 模块方式运行
"""

import unittest
import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 加载所有测试文件
    test_files = [
        'tests.test_linkages',
        'tests.test_geo',
        'tests.test_security',
    ]

    loaded = 0
    for tf in test_files:
        try:
            suite.addTests(loader.loadTestsFromName(tf))
            loaded += 1
        except Exception as e:
            print(f"  [SKIP] {tf}: {e}")

    print(f"\n{'=' * 60}")
    print(f"AIShield Test Suite")
    print(f"Loaded {loaded}/{len(test_files)} test modules")
    print(f"{'=' * 60}\n")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出摘要
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n{'=' * 60}")
    print(f"AIShield Test Suite Summary")
    print(f"{'=' * 60}")
    print(f"Total:    {result.testsRun}")
    print(f"Passed:   {passed}")
    print(f"Failed:   {len(result.failures)}")
    print(f"Errors:   {len(result.errors)}")
    print(f"Skipped:  {len(result.skipped)}")
    print(f"{'=' * 60}")

    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        if result.failures:
            print(f"\n--- Failures ({len(result.failures)}) ---")
            for test, traceback in result.failures:
                print(f"  FAIL: {test}")
        if result.errors:
            print(f"\n--- Errors ({len(result.errors)}) ---")
            for test, traceback in result.errors:
                print(f"  ERROR: {test}")

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
