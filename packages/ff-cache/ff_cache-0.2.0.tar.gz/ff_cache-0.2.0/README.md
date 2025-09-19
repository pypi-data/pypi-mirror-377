# ff-cache

一个简洁易用的 cache 封装库。

## 主要功能

- 通过注解`cache`来对函数执行结果进行缓存处理
- 支持对缓存进行标签分组管理
- 支持 memory / redis 缓存
- 支持自定义缓存逻辑(缓存key、根据结果动态计算缓存时间)

## 安装

```bash
pip install ff-cache
```

## 快速开始

```python
from ff_cache import ContextManager, MemoryCache, cache
from ff_cache.redis import RedisCache


redis_url = "redis://localhost:6379/0"
ContextManager.init(cache=RedisCache(url=redis_url))

@cache()
def hello_world():
    """
    """
    print("function executed.")
    return "hello world"


if __name__ == '__main__':
    print(hello_world()) # 第一次执行，控制台打印出：function executed.
    print("---------------------------------")
    print(hello_world()) # 第二次执行，控制台没有打印：function executed. 说明缓存成功
```

## 更多示例

请参考 `tests` 目录下的用例。

## 贡献指南

欢迎提交 Issue 或 PR，完善功能或修复问题。请确保代码风格与项目保持一致，并补充必要的测试。

## License

MIT