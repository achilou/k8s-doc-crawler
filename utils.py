import time
import functools

from logger import get_logger

logger = get_logger(__name__)

def atimeit(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Time taken by [{func.__name__}]: {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def aretry(max_retries=3):
    def decorator(func):
        @functools.wraps(func)  
        async def wrapper(*args, **kwargs):
            # logger.info(f"Retrying {func.__name__} up to {max_retries} times")
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.warning(f"Retrying {func.__name__} due to {e} (retry {retries}/{max_retries})")
                    if retries >= max_retries:
                        logger.error(f"Failed to execute {func.__name__} after {max_retries} retries. Last exception: {e}")
                        raise
        return wrapper
    return decorator
