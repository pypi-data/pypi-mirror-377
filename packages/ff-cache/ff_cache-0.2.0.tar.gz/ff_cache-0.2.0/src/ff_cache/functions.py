import hashlib
from datetime import datetime
from collections.abc import MutableMapping
from .constant import DATETIME_FORMAT


def md5_key_builder(ctx):
    """
    计算 MD5 哈希值
    :param ctx 缓存上下文参数
    :return md5 hash值
    """
    func = ctx.get("func", {})
    args = ctx.get("params", {}).get("args", [])
    kwargs = ctx.get("params", {}).get("kwargs", {})

    combined = (
        ''.join(f"{k}={v}" for k, v in func.items())
        + ''.join(str(arg) for arg in args) 
        + ''.join(f"{k}={v}" for k, v in kwargs.items())
    )

    md5_hash = hashlib.md5()
    md5_hash.update(combined.encode())
    return md5_hash.hexdigest()


def ttl_from_result(ctx):
    """
    计算缓存过期时间
    :param ctx 缓存上下文参数
    :return 缓存时间
    """
    now = datetime.now()
    result = ctx.get('result')

    if not result:
        return 0

    if isinstance(result, MutableMapping) and 'ttl' in result:
        return int(result.get('ttl'))
    
    if isinstance(result, MutableMapping) and 'expires_in' in result:
        return int(result.get("expires_in"))

    if hasattr(result, 'ttl'):
        return int(getattr(result, 'ttl'))
    
    if hasattr(result, 'expires_in'):
        return int(getattr(result, 'expires_in'))

    try:
        if isinstance(result, MutableMapping) and 'expired_at' in result:
            expired_at = result['expired_at']

            if isinstance(expired_at, str):
                expired_at: datetime = datetime.strptime(expired_at, DATETIME_FORMAT)
            
            if isinstance(expired_at, datetime):
                seconds = int((expired_at - now).total_seconds())
                return seconds if seconds > 0 else 0
        
        if hasattr(result, 'expired_at'):
            expired_at = getattr(result, 'expired_at')

            if isinstance(expired_at, str):
                expired_at: datetime = datetime.strptime(expired_at, DATETIME_FORMAT)
            
            if isinstance(expired_at, datetime):
                seconds = int((expired_at - now).total_seconds())
                return seconds if seconds > 0 else 0
    except:
        pass

    return 0