
# 将python函数翻译为c++函数并运行
## 1. 安装
```
pip install l0n0lc
```
## 2. hello_world.py
```python
import l0n0lc as lc
import math


@lc.映射函数(math.ceil, ['<cmath>'])
def cpp_ceil(v):
    return f'std::ceil({lc.toCString(v)});'


@lc.映射函数(print, ['<iostream>'])
def cpp_cout(*args):
    code = f'std::cout'
    for arg in args:
        code += f'<< {lc.toCString(arg)} << " "'
    code += '<< std::endl;'
    return code


def py_cin(v):
    pass


@lc.映射函数(py_cin, ['<iostream>'])
def cpp_cin(v):
    return f'std::cout << u8"请输入>>>"; std::cin >> {v};'


@lc.直接调用函数
def test_直接调用():
    return 123


def test_other_fn(a: int, b: int) -> int:
    return a - b


@lc.jit()
def test编译的函数(a: int, b: int) -> int:
    return a * b


@lc.映射类型('std::vector<int>', ['<vector>'])
class CppVectorInt:
    def push_back(self, v):
        pass

    def size(self):
        return 0

    def __getitem__(self, key):
        return 0


@lc.jit()
def jit_all_ops(a: int, b: int) -> int:
    # 常量与基础赋值
    x = 42
    y: int = a + b
    z = 3.14
    flag = True
    nums = [1, 2, 3]
    tup = (4, 5)
    mp = {1: 10, 2: 20}

    # 一元运算
    pos = +a
    neg = -b
    inv = ~a
    not_flag = not flag

    # 二元运算
    add = a + b
    sub = a - b
    mul = a * b
    div = a / (b if b != 0 else 1)
    mod = a % (b if b != 0 else 1)
    band = a & b
    bor = a | b
    bxor = a ^ b
    lshift = a << 1
    rshift = a >> 1

    # 比较运算
    cmp1 = a == b
    cmp2 = a != b
    cmp3 = a < b
    cmp4 = a <= b
    cmp5 = a > b
    cmp6 = a >= b

    # 逻辑运算与三元表达式
    logic_and = cmp1 and cmp2
    logic_or = cmp3 or cmp4
    ternary = a if a > b else b

    # if / else
    if a > b:
        y += 1
    else:
        y -= 1

    # for 循环 range
    for i in range(3):
        y += i

    # for 循环 列表
    for v in nums:
        y += v
        if v == 2:
            continue
        if v == 3:
            break

    # while 循环
    count = 0
    while count < 2:
        y += count
        count += 1

    # 增强赋值
    y += 5
    y -= 1
    y *= 2
    y //= 2
    y %= 10
    y &= 7
    y |= 3
    y ^= 1
    y <<= 1
    y >>= 1

    # 下标访问
    first_num = nums[0]
    mp_val = mp[1]
    y += first_num + mp_val

    vector = CppVectorInt()
    vector.push_back(count)
    vector.push_back(y)
    for i in range(vector.size()):
        print('vector->', i, '=', vector[i])
    return y

@lc.jit(每次运行都重新编译=True)
def test_add(a: int, b: int) -> int:
    if a > 1:
        return a + b
    for i in range(1, 10, 2):
        a += i
    for i in [1, 2, 3]:
        a += i
    a = math.ceil(12.5)
    cc = {'a': 1, 'b': 2}
    cc['c'] = 3
    print('输出map:')
    for ii in cc:
        print(ii.first, ii.second)  # type: ignore
    aa = [1, 3, 2]
    aa[0] = 134
    print('输出list:')
    for i in range(3):
        print(i, aa[i])
    print('Hello World', a, b)
    print('test_other_fn', test_other_fn(a, b))
    print('test编译的函数', test编译的函数(a, b))

    print('测试所有操作:')
    jit_all_ops(a, b)

    v = 0
    vv = True and (False or 1)
    print('vv:', vv)
    print('测试while:')
    while (vv):
        py_cin(v)
        if v > 100:
            break
        else:
            print('输入的', v, '小于等于100')
    return a + b + 1 + test_直接调用() + v


print('结果:', test_add(1, 3))

```

## 3. 运行hello_world.py
```
uv run tests/hello_world.py
# 输入: b'1\n2\n100\n101\n'
```
```bash
输出map: 
c 3 
a 1 
b 2 
输出list: 
0 134 
1 3 
2 2 
Hello World 13 3 
test_other_fn 10 
test编译的函数 39 
测试所有操作: 
vector-> 0 = 2 
vector-> 1 = 13 
vv: 1 
测试while: 
请输入>>>输入的 1 小于等于100 
请输入>>>输入的 2 小于等于100 
请输入>>>输入的 100 小于等于100 
请输入>>>结果: 241

```

## 4. 查看输出文件
```bash
ls -al ./l0n0lcoutput

```
## 5. jit_all_ops_@0ec883892076cd03.cpp
```c++
#include "jit_all_ops_@0ec883892076cd03.h"
extern "C" int16_t jit_all_ops (int16_t a, int16_t b)
{
  auto x = 42;
  auto y = ((int16_t)(a + b));
  auto z = 3.14;
  auto flag = true;
  int16_t nums[] = {1,2,3};
  int16_t tup[] = {4,5};
  std::unordered_map<int16_t, int16_t> mp = {{ 1, 10 },{ 2, 20 }};
  auto pos = +a;
  auto neg = -b;
  auto inv = ~a;
  auto not_flag = !flag;
  auto add = a + b;
  auto sub = a - b;
  auto mul = a * b;
  auto div = a / ((b != 0) ? (b) : (1));
  auto mod = a % ((b != 0) ? (b) : (1));
  auto band = a & b;
  auto bor = a | b;
  auto bxor = a ^ b;
  auto lshift = a << 1;
  auto rshift = a >> 1;
  auto cmp1 = (a == b);
  auto cmp2 = (a != b);
  auto cmp3 = (a < b);
  auto cmp4 = (a <= b);
  auto cmp5 = (a > b);
  auto cmp6 = (a >= b);
  auto logic_and = cmp1&&cmp2;
  auto logic_or = cmp3||cmp4;
  auto ternary = ((a > b) ? (a) : (b));
  if ((a > b))
  {
    y = y + 1;
  }

  else
  {
    y = y - 1;
  }

  for (int64_t i = 0; i < 3; ++i)
  {
    y = y + i;
  }

  for (auto v : nums)
  {
    y = y + v;
    if ((v == 2))
    {
      continue;
    }

    if ((v == 3))
    {
      break;
    }

  }

  auto count = 0;
  while ((count < 2))
  {
    y = y + count;
    count = count + 1;
  }

  y = y + 5;
  y = y - 1;
  y = y * 2;
  y = y / 2;
  y = y % 10;
  y = y & 7;
  y = y | 3;
  y = y ^ 1;
  y = y << 1;
  y = y >> 1;
  auto first_num = nums[0];
  auto mp_val = mp[1];
  y = y + first_num + mp_val;
  auto vector = std::vector<int>();
  vector.push_back(count);
  vector.push_back(y);
  for (int64_t i = 0; i < vector.size(); ++i)
  {
    std::cout<< u8"vector->" << " "<< i << " "<< u8"=" << " "<< vector[i] << " "<< std::endl;;
  }

  return y;
}

```
## 6. jit_all_ops_@0ec883892076cd03.h
```c++
#pragma once
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
extern "C" int16_t jit_all_ops (int16_t a, int16_t b);
```
## 7. test_add_@122c4be59097d472.cpp
```c++
#include "test_add_@122c4be59097d472.h"
extern "C" int16_t test_add (int16_t a, int16_t b)
{
  if ((a > 1))
  {
    return a + b;
  }

  for (int64_t i = 1; i < 10; i += 2)
  {
    a = a + i;
  }

  for (auto i : {1,2,3})
  {
    a = a + i;
  }

  a = std::ceil(12.5);;
  std::unordered_map<std::string, int16_t> cc = {{ u8"a", 1 },{ u8"b", 2 }};
  cc[u8"c"] = 3;
  std::cout<< u8"输出map:" << " "<< std::endl;;
  for (auto ii : cc)
  {
    std::cout<< ii.first << " "<< ii.second << " "<< std::endl;;
  }

  int16_t aa[] = {1,3,2};
  aa[0] = 134;
  std::cout<< u8"输出list:" << " "<< std::endl;;
  for (int64_t i = 0; i < 3; ++i)
  {
    std::cout<< i << " "<< aa[i] << " "<< std::endl;;
  }

  std::cout<< u8"Hello World" << " "<< a << " "<< b << " "<< std::endl;;
  std::cout<< u8"test_other_fn" << " "<< test_other_fn(a,b) << " "<< std::endl;;
  std::cout<< u8"test编译的函数" << " "<< function_74657374e7bc96e8af91e79a84e587bde695b0(a,b) << " "<< std::endl;;
  std::cout<< u8"测试所有操作:" << " "<< std::endl;;
  jit_all_ops(a,b);
  auto v = 0;
  auto vv = true&&false||1;
  std::cout<< u8"vv:" << " "<< vv << " "<< std::endl;;
  std::cout<< u8"测试while:" << " "<< std::endl;;
  while (vv)
  {
    std::cout << u8"请输入>>>"; std::cin >> v;;
    if ((v > 100))
    {
      break;
    }

    else
    {
      std::cout<< u8"输入的" << " "<< v << " "<< u8"小于等于100" << " "<< std::endl;;
    }

  }

  return a + b + 1 + 123 + v;
}

```
## 8. test_add_@122c4be59097d472.h
```c++
#pragma once
#include "jit_all_ops_@0ec883892076cd03.h"
#include "test_other_fn_@75fdd928ab58a8e3.h"
#include "test编译的函数_@3bf4501e0408a243.h"
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
extern "C" int16_t test_add (int16_t a, int16_t b);
```
## 9. test_other_fn_@75fdd928ab58a8e3.cpp
```c++
#include "test_other_fn_@75fdd928ab58a8e3.h"
extern "C" int16_t test_other_fn (int16_t a, int16_t b)
{
  return a - b;
}

```
## 10. test_other_fn_@75fdd928ab58a8e3.h
```c++
#pragma once
#include <cstdint>
#include <string>
extern "C" int16_t test_other_fn (int16_t a, int16_t b);
```
## 11. test编译的函数_@3bf4501e0408a243.cpp
```c++
#include "test编译的函数_@3bf4501e0408a243.h"
extern "C" int16_t /*test编译的函数*/ function_74657374e7bc96e8af91e79a84e587bde695b0 (int16_t a, int16_t b)
{
  return a * b;
}

```
## 12. test编译的函数_@3bf4501e0408a243.h
```c++
#pragma once
#include <cstdint>
#include <string>
extern "C" int16_t /*test编译的函数*/ function_74657374e7bc96e8af91e79a84e587bde695b0 (int16_t a, int16_t b);
```
