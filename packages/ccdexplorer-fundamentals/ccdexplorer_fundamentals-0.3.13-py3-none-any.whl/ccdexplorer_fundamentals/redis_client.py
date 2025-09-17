#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import suppress
from typing import Callable, Dict, List, Optional, Tuple

from env import REDIS_URL, RUN_LOCAL, RUN_ON_NET
from pydantic import BaseModel, computed_field
from redis.asyncio import Redis
from redis.exceptions import ResponseError


class Settings(BaseModel):
    processor: str

    redis_url: Optional[str] = REDIS_URL

    stream_prefix: str = os.getenv("STREAM_PREFIX", "blocks")
    group_prefix: str = os.getenv("GROUP_PREFIX", "workers")

    block_ms: int = int(os.getenv("XREAD_BLOCK_MS", "5000"))
    count: int = int(os.getenv("XREAD_COUNT", "32"))
    reclaim_idle_ms: int = int(os.getenv("RECLAIM_MIN_IDLE_MS", "2000"))
    reclaim_batch: int = int(os.getenv("RECLAIM_BATCH", "200"))
    trim_maxlen: int = int(os.getenv("STREAM_TRIM_MAXLEN", "100000"))
    health_log_secs: int = int(os.getenv("HEALTH_LOG_SECS", "300"))
    test_xadd_on_boot: str = os.getenv("TEST_XADD_ON_BOOT", "false").lower()

    model_config = {"arbitrary_types_allowed": True}

    @computed_field
    @property
    def consumer(self) -> str:
        consumer: str = os.getenv(
            "CONSUMER", f"{RUN_ON_NET}-{self.processor}-{RUN_LOCAL}"
        )
        return consumer


class RedisClient:
    def __init__(self, processor: str):
        self.processor = processor
        self.settings = Settings(processor=processor)
        self.stream = (
            f"{self.settings.stream_prefix}:{self.settings.processor}:{RUN_ON_NET}"
        )
        self.group = (
            f"{self.settings.group_prefix}:{self.settings.processor}:{RUN_ON_NET}"
        )
        self.dlq_stream = f"{self.stream}:dlq"
        self.r = Redis.from_url(self.settings.redis_url, db=0, decode_responses=False)  # type: ignore

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def ensure_group(self) -> None:
        try:
            await self.r.xgroup_create(self.stream, self.group, id="0-0", mkstream=True)
            print(f"[{self.settings.processor}] group created", file=sys.stderr)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    async def dead_letter(
        self, msg_id: bytes | str, fields: Dict[bytes, bytes], err: Exception
    ) -> None:
        data = fields.get(b"data") or fields.get("data") or b""  # type: ignore
        if not isinstance(data, (bytes, bytearray)):
            data = str(data).encode("utf-8", errors="replace")
        await self.r.xadd(
            self.dlq_stream,
            {
                b"data": data,
                b"error": str(err).encode("utf-8", errors="replace"),
                b"orig_id": (
                    msg_id
                    if isinstance(msg_id, (bytes, bytearray))
                    else str(msg_id).encode()
                ),
                b"consumer": self.settings.consumer.encode(),
            },
        )

    async def validate_payload(self, fields: Dict[bytes, bytes]) -> dict:
        raw = fields.get(b"data") or fields.get("data")  # type: ignore
        if not raw:
            raise ValueError("missing 'data' field")
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
            return payload
        except Exception as e:
            raise ValueError(f"invalid JSON in 'data': {e}") from e

    async def read_batch(
        self, streams: Dict[str, str], *, count: int, block_ms: int
    ) -> List[Tuple[bytes, List[Tuple[bytes, Dict[bytes, bytes]]]]]:
        """Wrapper around XREADGROUP returning [] on timeout."""
        try:
            resp = await self.r.xreadgroup(
                self.group, self.settings.consumer, streams, count=count, block=block_ms  # type: ignore
            )
            return resp or []
        except ResponseError as e:
            # if group was reset or stream deleted, surface clearly
            print(
                f"[{self.settings.processor}] xreadgroup error: {e!r}", file=sys.stderr
            )
            return []

    async def claim_all_pending(self, handle_payload_callable: Callable) -> int:
        total = 0
        last_id = "0-0"
        while True:
            res = await self.r.xautoclaim(
                name=self.stream,
                groupname=self.group,
                consumername=self.settings.consumer,
                min_idle_time=0,
                start_id=last_id,
                count=self.settings.reclaim_batch,
            )
            if isinstance(res, (list, tuple)):
                if len(res) == 2:
                    next_id, messages = res
                else:
                    next_id, messages, _ = res
            else:
                print(
                    f"[{self.settings.processor}] xautoclaim non-iterable: {res!r}",
                    file=sys.stderr,
                )
                break

            if not messages:
                break

            for msg_id, fields in messages:
                try:
                    payload = await self.validate_payload(fields)
                    if payload:
                        await handle_payload_callable(payload)
                except Exception as e:
                    print(
                        f"[{self.settings.processor}] claim_all error {e!r} id={msg_id}",
                        file=sys.stderr,
                    )
                    await self.dead_letter(msg_id, fields, e)
                    await self.r.xack(self.stream, self.group, msg_id)
                    await self.r.xdel(self.stream, msg_id)
                else:
                    await self.r.xack(self.stream, self.group, msg_id)
                total += 1

            next_id = (
                next_id.decode() if isinstance(next_id, (bytes, bytearray)) else next_id
            )
            if next_id == last_id:
                break
            last_id = next_id
        return total

    async def reclaim_stuck(self, handle_payload_callable: Callable) -> int:
        reclaimed = 0
        last_id = "0-0"
        while True:
            res = await self.r.xautoclaim(
                name=self.stream,
                groupname=self.group,
                consumername=self.settings.consumer,
                min_idle_time=self.settings.reclaim_idle_ms,
                start_id=last_id,
                count=self.settings.reclaim_batch,
            )
            if isinstance(res, (list, tuple)):
                if len(res) == 2:
                    next_id, messages = res
                else:
                    next_id, messages, _ = res
            else:
                print(
                    f"[{self.settings.processor}] xautoclaim non-iterable response: {res!r}",
                    file=sys.stderr,
                )
                break

            if not messages:
                break

            for msg_id, fields in messages:
                try:
                    payload = await self.validate_payload(fields)
                    if payload:
                        await handle_payload_callable(payload)
                except Exception as e:
                    print(
                        f"[{self.settings.processor}] process error {e!r} id={msg_id}",
                        file=sys.stderr,
                    )
                    await self.dead_letter(msg_id, fields, e)
                    await self.r.xack(self.stream, self.group, msg_id)
                    await self.r.xdel(self.stream, msg_id)
                else:
                    await self.r.xack(self.stream, self.group, msg_id)
                reclaimed += 1

            next_id = (
                next_id.decode() if isinstance(next_id, (bytes, bytearray)) else next_id
            )
            if next_id == last_id:
                break
            last_id = next_id
        return reclaimed

    async def maybe_trim(self):
        if self.settings.trim_maxlen > 0:
            await self.r.xtrim(
                self.stream, maxlen=self.settings.trim_maxlen, approximate=True
            )

    async def health_log_task(self):
        while True:
            try:
                groups = await self.r.xinfo_groups(self.stream)
                consumers = await self.r.xinfo_consumers(self.stream, self.group)
                print(f"[health] groups={groups}")
                print(f"[health] consumers={consumers}")
            except Exception as e:
                print(f"[health] error: {e!r}")
            await asyncio.sleep(self.settings.health_log_secs)

    async def _process_one(
        self,
        msg_id: bytes | str,
        fields: Dict[bytes, bytes],
        handle_payload: Callable[[Dict], "asyncio.Future"],
    ) -> None:
        try:
            payload = await self.validate_payload(fields)
            if payload:
                await handle_payload(payload)
        except Exception as e:
            # DLQ + ACK + XDEL so poison doesn't starve the loop
            print(
                f"[{self.settings.processor}] process error {e!r} id={msg_id}",
                file=sys.stderr,
            )
            await self.dead_letter(msg_id, fields, e)
            await self.r.xack(self.stream, self.group, msg_id)
            await self.r.xdel(self.stream, msg_id)
        else:
            await self.r.xack(self.stream, self.group, msg_id)

    # --- read a batch (my PEL first, then new) and process it ---
    async def pump_once(
        self,
        handle_payload: Callable[[Dict], "asyncio.Future"],
    ) -> int:
        processed = 0

        # 1) drain this consumer's PEL
        resp = await self.read_batch(
            {self.stream: "0"}, count=self.settings.count, block_ms=1
        )
        entries: List[Tuple[bytes, Dict[bytes, bytes]]] = []
        if resp:
            _, entries = resp[0]
        if entries:
            for msg_id, fields in entries:
                await self._process_one(msg_id, fields, handle_payload)
                processed += 1
            return processed

        # 2) read new messages
        resp = await self.read_batch(
            {self.stream: ">"},
            count=self.settings.count,
            block_ms=self.settings.block_ms,
        )
        if resp:
            _, entries = resp[0]
        if entries:
            for msg_id, fields in entries:
                await self._process_one(msg_id, fields, handle_payload)
                processed += 1
            return processed

        # 3) try reclaiming stuck ones
        reclaimed = await self.reclaim_stuck(handle_payload)
        if reclaimed == 0:
            await self.maybe_trim()
        return processed + reclaimed

    # --- initial boot sequence: ensure group, optional poke, sweep PEL ---
    async def boot(self, handle_payload: Callable[[Dict], "asyncio.Future"]) -> None:
        await self.ensure_group()

        # kick delivery once (non-blocking)
        boot = await self.read_batch(
            {self.stream: ">"}, count=self.settings.count, block_ms=1
        )
        print(
            f"[dbg] boot read returned {len(boot[0][1]) if boot else 0} entries",
            file=sys.stderr,
        )

        # claim any orphaned PEL
        claimed = await self.claim_all_pending(handle_payload)
        print(
            f"[{self.settings.processor}] claimed {claimed} pending at startup",
            file=sys.stderr,
        )

    # --- background health logger (start/stop) ---
    def start_health(self) -> None:
        if not hasattr(self, "_health_task") or self._health_task is None:
            self._health_task = asyncio.create_task(self.health_log_task())

    async def close(self) -> None:
        # stop health task and close redis
        if hasattr(self, "_health_task") and self._health_task:
            self._health_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._health_task
        await self.r.aclose()

    # --- full run loop (forever) ---
    async def run(self, handle_payload: Callable) -> None:
        await self.boot(handle_payload)
        self.start_health()
        while True:
            await self.pump_once(handle_payload)
