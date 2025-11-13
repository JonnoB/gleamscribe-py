#!/usr/bin/env python3
from tests.test_real_world import transcribe_mode, REAL_WORLD_TEST_CASES

test_case = REAL_WORLD_TEST_CASES[0]
result = transcribe_mode(test_case['mode'], test_case['input'])
expected = test_case['expected']

print(f"Expected length: {len(expected)}")
print(f"Got length: {len(result)}")
print(f"Match: {result == expected}")

if result != expected:
    for i in range(max(len(expected), len(result))):
        if i >= len(expected):
            print(f"Position {i}: EXTRA in result: {hex(ord(result[i]))}")
        elif i >= len(result):
            print(f"Position {i}: MISSING from result, expected: {hex(ord(expected[i]))}")
        elif expected[i] != result[i]:
            print(f"Position {i}: expected {hex(ord(expected[i]))}, got {hex(ord(result[i]))}")
else:
    print("\n🎉 PERFECT MATCH! 100% Ruby parity achieved!")
