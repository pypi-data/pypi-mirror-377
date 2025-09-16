
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
    v = 0
    vv = True
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
请输入>>>输入的 1 小于等于100 
请输入>>>输入的 2 小于等于100 
请输入>>>输入的 100 小于等于100 
请输入>>>结果: 241

```

## 4. 查看输出文件
```bash
ls -al ./l0n0lcoutput
total 96
drwxr-xr-x  2 root root  4096 Sep 16 01:38 .
drwxrwxrwx 11 1000 1000  4096 Sep 16 01:36 ..
-rw-r--r--  1 root root  1252 Sep 16 01:38 test_add_@05ade4b088e9b383.cpp
-rw-r--r--  1 root root   246 Sep 16 01:38 test_add_@05ade4b088e9b383.h
-rwxr-xr-x  1 root root 29904 Sep 16 01:38 test_add_@05ade4b088e9b383.so
-rw-r--r--  1 root root   121 Sep 16 01:38 test_other_fn_@75fdd928ab58a8e3.cpp
-rw-r--r--  1 root root    93 Sep 16 01:38 test_other_fn_@75fdd928ab58a8e3.h
-rwxr-xr-x  1 root root 15616 Sep 16 01:38 test_other_fn_@75fdd928ab58a8e3.so
-rw-r--r--  1 root root   185 Sep 16 01:36 test编译的函数_@3bf4501e0408a243.cpp
-rw-r--r--  1 root root   151 Sep 16 01:36 test编译的函数_@3bf4501e0408a243.h
-rwxr-xr-x  1 root root 15656 Sep 16 01:36 test编译的函数_@3bf4501e0408a243.so

```
## 5. test_add_@05ade4b088e9b383.cpp
```c++
#include "test_add_@05ade4b088e9b383.h"
extern "C" int64_t test_add (int64_t a, int64_t b)
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
  std::unordered_map<std::string, int64_t> cc = {{ u8"a", 1 },{ u8"b", 2 }};
  cc[u8"c"] = 3;
  std::cout<< u8"输出map:" << " "<< std::endl;
  for (auto ii : cc)
  {
    std::cout<< ii.first << " "<< ii.second << " "<< std::endl;
  }

  int64_t aa[] = {1,3,2};
  aa[0] = 134;
  std::cout<< u8"输出list:" << " "<< std::endl;
  for (int64_t i = 0; i < 3; ++i)
  {
    std::cout<< i << " "<< aa[i] << " "<< std::endl;
  }

  std::cout<< u8"Hello World" << " "<< a << " "<< b << " "<< std::endl;
  std::cout<< u8"test_other_fn" << " "<< test_other_fn(a,b) << " "<< std::endl;
  std::cout<< u8"test编译的函数" << " "<< function_74657374e7bc96e8af91e79a84e587bde695b0(a,b) << " "<< std::endl;
  auto v = 0;
  auto vv = true;
  while (vv)
  {
    std::cout << u8"请输入>>>"; std::cin >> v;
    if ((v > 100))
    {
      break;
    }

    {
      std::cout<< u8"输入的" << " "<< v << " "<< u8"小于等于100" << " "<< std::endl;
    }

  }

  return a + b + 1 + 123 + v;
}

```
## 6. test_add_@05ade4b088e9b383.h
```c++
#include "test_other_fn_@75fdd928ab58a8e3.h"
#include "test编译的函数_@3bf4501e0408a243.h"
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
extern "C" int64_t test_add (int64_t a, int64_t b);
```
## 7. test_other_fn_@75fdd928ab58a8e3.cpp
```c++
#include "test_other_fn_@75fdd928ab58a8e3.h"
extern "C" int64_t test_other_fn (int64_t a, int64_t b)
{
  return a - b;
}

```
## 8. test_other_fn_@75fdd928ab58a8e3.h
```c++
#include <cstdint>
#include <string>
extern "C" int64_t test_other_fn (int64_t a, int64_t b);
```
## 9. test编译的函数_@3bf4501e0408a243.cpp
```c++
#include "test编译的函数_@3bf4501e0408a243.h"
extern "C" int64_t /*test编译的函数*/ function_74657374e7bc96e8af91e79a84e587bde695b0 (int64_t a, int64_t b)
{
  return a * b;
}

```
## 10. test编译的函数_@3bf4501e0408a243.h
```c++
#include <cstdint>
#include <string>
extern "C" int64_t /*test编译的函数*/ function_74657374e7bc96e8af91e79a84e587bde695b0 (int64_t a, int64_t b);
```
