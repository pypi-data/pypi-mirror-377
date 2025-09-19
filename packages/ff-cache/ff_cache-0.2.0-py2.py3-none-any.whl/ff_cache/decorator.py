import inspect
from typing import Callable, List, Union
from functools import wraps

from .context import ContextManager
from .cache import CacheItem, Cache


def cache(
    cache: Cache = None,
    key: Union[Callable[..., str], str] = None, 
    ttl: Union[Callable[..., int], int] = None,
    tags: List[str] = []
):
    """
    缓存装饰器

    Args:
        cache: 缓存实例
        key: 缓存键名
        ttl: 过期时间
        tags: 缓存标签

    Returns:
        缓存包装函数对象
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _cache_func(
                func=func, cache=cache, key=key, ttl=ttl, tags=tags, *args, **kwargs
            )
        return wrapper        
    return decorator


def _cache_func(
    *args,
    func,
    cache: Cache, 
    key: Union[Callable[..., str], str],
    ttl: Union[Callable[..., int], int] = 0,
    tags: List[str] = [],
    **kwargs
):
    ctx = {
        "params": {
            "args": args,
            "kwargs": kwargs
        },
        "func": {
            "__qualname__": func.__qualname__
        }
    }

    key = key if key else ContextManager.get_key_builder()
    ttl = ttl if ttl else ContextManager.get_ttl()
    cache = cache if cache else ContextManager.get_cache()

    _key = key if isinstance(key, str) else key(ctx)

    if cache.has(key=_key):
        return cache.get(key=_key).value

    result = func(*args, **kwargs)
    
    ctx['result'] = result
    _ttl = ttl if isinstance(ttl, int) else ttl(ctx)

    cache_item = CacheItem(
        key=_key,
        value=result,
        ttl=_ttl,
        tags=tags
    )

    cache.save(cache_item=cache_item)
    return cache_item.value
