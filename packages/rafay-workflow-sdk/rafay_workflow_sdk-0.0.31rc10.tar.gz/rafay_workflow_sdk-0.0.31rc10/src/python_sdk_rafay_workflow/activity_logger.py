import asyncio
from io import BytesIO
from logging.handlers import MemoryHandler

import httpx

from .const import WorkflowTokenHeader


class ActivityLogHandler(MemoryHandler):
    def __init__(
            self,
            endpoint: str,
            token: str,
            flush_interval: int = 10,
            timeout: int = 10,
            verify: bool = True,
            max_retries: int = 3,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.token = token
        self.flush_interval = flush_interval
        self.timeout = timeout
        self.verify = verify
        self.max_retries = max_retries

        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

        # one async client per handler
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            verify=verify,
        )

        # spawn background flush loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            self._task = asyncio.create_task(self._start_upload())

    async def _send_logs(self, payload: bytes) -> httpx.Response:
        files = {"content": ("stdout", BytesIO(payload), "text/plain")}
        return await self.client.post(
            f"{self.endpoint}?append=true",
            headers={WorkflowTokenHeader: self.token},
            files=files,
        )

    def flush(self):
        """Schedule an async flush when buffer capacity is reached."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.async_flush())
        except RuntimeError:
            # no running loop
            pass

    async def async_flush(self):
        """Flush buffer contents asynchronously."""
        async with self._lock:
            if not self.buffer:
                return

            buf = [self.format(record) for record in self.buffer]
            payload = ("\n".join(buf) + "\n").encode("utf-8")

            attempt = 0
            while attempt < self.max_retries:
                try:
                    resp = await self._send_logs(payload)
                    if resp.status_code == 200:
                        self.buffer.clear()
                        return
                except Exception as _:
                    pass
                attempt += 1
                await asyncio.sleep(1)

            print(
                f"[ActivityLogHandler] Failed to send logs to {self.endpoint} "
                f"after {self.max_retries} attempts"
            )

    async def _start_upload(self):
        """Background loop like Go's startUpload (ticker-based)."""
        try:
            while not self._stop_event.is_set():
                # Use wait_for with timeout instead of sleep to respond faster to stop events
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=self.flush_interval)
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    # Timeout means it's time to flush
                    await self.async_flush()
        except asyncio.CancelledError:
            pass
        finally:
            # always do one last flush
            await self.async_flush()

    async def close(self) -> None:
        """Stop ticker loop and close client gracefully."""
        # Signal the background loop to exit
        self._stop_event.set()

        # If no background task exists, still ensure remaining logs are flushed below
        if self._task:
            try:
                # wait for graceful completion up to close_wait
                await asyncio.wait_for(self._task, timeout=2.0)
            except asyncio.TimeoutError:
                # task didn't stop in time — cancel it
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            except Exception:
                pass

        try:
            await self.async_flush()
        except Exception:
            pass

        # close httpx client
        if not self.client.is_closed:
            try:
                await self.client.aclose()
            except Exception:
                pass
