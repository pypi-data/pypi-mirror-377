# encoding: utf-8
import asyncio


class AsyncTimeoutLock:
    def __init__(self, loop=None):
        self._lock = asyncio.Lock(loop=loop)

    async def acquire(self, timeout=None):
        """尝试获取锁，支持超时时间。

        Args:
            timeout (float or None): 超时时间，以秒为单位。如果为 None，则不设置超时。

        Returns:
            bool: 如果成功获取锁，则返回 True；如果因为超时未获取锁，则返回 False。
        """
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def release(self):
        """释放锁。"""
        self._lock.release()

    # 使用示例


async def test_async_timeout_lock():
    lock = AsyncTimeoutLock()

    # 假设这是第一个协程，它将成功获取锁
    async def coro1():
        print("coro1: trying to acquire lock")
        await lock.acquire(timeout=1)
        print("coro1: lock acquired")
        # 模拟一些处理时间
        await asyncio.sleep(2)
        print("coro1: releasing lock")
        await lock.release()

        # 假设这是第二个协程，它将在超时后放弃获取锁

    async def coro2():
        print("coro2: trying to acquire lock")
        if not await lock.acquire(timeout=1):
            print("coro2: lock acquisition timed out")
        else:
            print("coro2: lock acquired (shouldn't happen)")
            await lock.release()

            # 并发运行两个协程

    await asyncio.gather(coro1(), coro2())


# 运行测试
asyncio.run(test_async_timeout_lock())