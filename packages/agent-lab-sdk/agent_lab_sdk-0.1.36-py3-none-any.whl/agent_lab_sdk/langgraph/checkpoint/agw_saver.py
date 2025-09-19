from __future__ import annotations

import asyncio
import base64
import logging
import os
from contextlib import asynccontextmanager
from random import random
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Sequence, Tuple

import httpx
import orjson
from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
    get_checkpoint_metadata,
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.serde.types import ChannelProtocol
from .serde import Serializer

__all__ = ["AsyncAGWCheckpointSaver"]

logger = logging.getLogger(__name__)

TYPED_KEYS = ("type", "blob")


def _to_b64(b: bytes | None) -> str | None:
    return base64.b64encode(b).decode() if b is not None else None


def _b64decode_strict(s: str) -> bytes | None:
    """Возвращает bytes только если строка действительно корректная base64."""
    try:
        return base64.b64decode(s, validate=True)
    except Exception:
        return None


class AsyncAGWCheckpointSaver(BaseCheckpointSaver):
    """Persist checkpoints in Agent-Gateway с помощью `httpx` async client."""

    # ---------------------------- init / ctx -------------------------
    def __init__(
        self,
        base_url: str = "http://localhost",
        *,
        serde: SerializerProtocol | None = None,
        timeout: int | float = 10,
        api_key: str | None = None,
        extra_headers: Dict[str, str] | None = None,
        verify: bool = True,
    ):
        if not serde:
            base_serde: SerializerProtocol = Serializer()
            # опционально оборачиваем в AES по ENV
            _aes_key = (
                os.getenv("LANGGRAPH_AES_KEY")
                or os.getenv("AGW_AES_KEY")
                or os.getenv("AES_KEY")
            )
            if _aes_key:
                base_serde = EncryptedSerializer.from_pycryptodome_aes(
                    base_serde, key=_aes_key
                )
            serde = base_serde
        super().__init__(serde=serde)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.loop = asyncio.get_running_loop()

        self.headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            self.headers.update(extra_headers)
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            verify=verify,
            trust_env=True,
        )

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
        await self._client.aclose()

    # ----------------------- typed (de)serialize ---------------------
    def _encode_typed(self, value: Any) -> dict[str, Any]:
        """value -> {"type": str, "blob": base64str | null}"""
        t, b = self.serde.dumps_typed(value)
        return {"type": t, "blob": _to_b64(b)}

    def _decode_typed(self, obj: Any) -> Any:
        """{type, blob} | [type, blob] | legacy -> python."""
        # Новый формат: dict с ключами type/blob — только если blob валидная base64 или None
        if isinstance(obj, dict) and all(k in obj for k in TYPED_KEYS):
            t = obj.get("type")
            b64 = obj.get("blob")
            if b64 is None:
                return self.serde.loads_typed((t, None))
            if isinstance(b64, str):
                b = _b64decode_strict(b64)
                if b is not None:
                    return self.serde.loads_typed((t, b))
            # если невалидно — падаем ниже на общую обработку

        # Допускаем tuple/list вида [type, base64] — только при валидной base64
        if isinstance(obj, (list, tuple)) and len(obj) == 2 and isinstance(obj[0], str):
            t, b64 = obj
            if b64 is None and t == "empty":
                return self.serde.loads_typed((t, None))
            if isinstance(b64, str):
                b = _b64decode_strict(b64)
                if b is not None:
                    return self.serde.loads_typed((t, b))
            # иначе это не typed-пара

        # Если это строка — пробуем как base64 строго, затем как JSON-строку
        if isinstance(obj, str):
            b = _b64decode_strict(obj)
            if b is not None:
                try:
                    return self.serde.loads(b)
                except Exception:
                    pass
            try:
                return self.serde.loads(obj.encode())
            except Exception:
                return obj

        # dict/list -> считаем это уже JSON и грузим через serde
        if isinstance(obj, (dict, list)):
            try:
                return self.serde.loads(orjson.dumps(obj))
            except Exception:
                return obj

        # как есть пробуем через serde
        try:
            return self.serde.loads(obj)
        except Exception:
            return obj

    # ----------------------- config <-> api --------------------------
    def _to_api_config(self, cfg: RunnableConfig | None) -> Dict[str, Any]:
        if not cfg:
            return {}
        c = cfg.get("configurable", {})
        res: Dict[str, Any] = {
            "threadId": c.get("thread_id", ""),
            "checkpointNs": c.get("checkpoint_ns", ""),
        }
        if cid := c.get("checkpoint_id"):
            res["checkpointId"] = cid
        if ts := c.get("thread_ts"):
            res["threadTs"] = ts
        return res

    # --------------------- checkpoint (de)ser ------------------------
    def _encode_cp(self, cp: Checkpoint) -> Dict[str, Any]:
        channel_values = {
            k: self._encode_typed(v) for k, v in cp.get("channel_values", {}).items()
        }
        pending = []
        for item in cp.get("pending_sends", []) or []:
            try:
                channel, value = item
                pending.append({"channel": channel, **self._encode_typed(value)})
            except Exception:
                continue
        return {
            "v": cp["v"],
            "id": cp["id"],
            "ts": cp["ts"],
            "channelValues": channel_values,
            "channelVersions": cp["channel_versions"],
            "versionsSeen": cp["versions_seen"],
            "pendingSends": pending,
        }

    def _decode_cp(self, raw: Dict[str, Any]) -> Checkpoint:
        cv_raw = raw.get("channelValues") or {}
        channel_values = {k: self._decode_typed(v) for k, v in cv_raw.items()}
        ps_raw = raw.get("pendingSends") or []
        pending_sends = []
        for obj in ps_raw:
            # ожидаем {channel, type, blob}
            if isinstance(obj, dict) and "channel" in obj:
                ch = obj["channel"]
                typed = {k: obj[k] for k in obj.keys() if k in TYPED_KEYS}
                val = self._decode_typed(typed)
                pending_sends.append((ch, val))
            elif isinstance(obj, (list, tuple)) and len(obj) == 2:
                ch, val = obj
                pending_sends.append((ch, self._decode_typed(val)))

        return Checkpoint(
            v=raw["v"],
            id=raw["id"],
            ts=raw["ts"],
            channel_values=channel_values,
            channel_versions=raw["channelVersions"],
            versions_seen=raw["versionsSeen"],
            pending_sends=pending_sends,
        )

    def _decode_config(self, raw: Dict[str, Any] | None) -> Optional[RunnableConfig]:
        if not raw:
            return None
        return RunnableConfig(
            tags=raw.get("tags"),
            metadata=raw.get("metadata"),
            callbacks=raw.get("callbacks"),
            run_name=raw.get("run_name"),
            max_concurrency=raw.get("max_concurrency"),
            recursion_limit=raw.get("recursion_limit"),
            configurable=self._decode_configurable(raw.get("configurable") or {}),
        )

    def _decode_configurable(self, raw: Dict[str, Any]) -> dict[str, Any]:
        return {
            "thread_id": raw.get("threadId"),
            "thread_ts": raw.get("threadTs"),
            "checkpoint_ns": raw.get("checkpointNs"),
            "checkpoint_id": raw.get("checkpointId"),
        }

    # metadata (de)ser — передаём как есть (JSON-совместимый словарь)
    def _enc_meta(self, md: CheckpointMetadata) -> CheckpointMetadata:
        return md or {}

    def _dec_meta(self, md: Any) -> Any:
        return md

    # ------------------------ HTTP wrapper ---------------------------
    async def _http(self, method: str, path: str, **kw) -> httpx.Response:
        if "json" in kw:
            payload = kw.pop("json")
            kw["data"] = orjson.dumps(payload)
            logger.debug("AGW HTTP payload: %s", kw["data"].decode())
        return await self._client.request(method, path, **kw)

    # -------------------- api -> CheckpointTuple ----------------------
    def _to_tuple(self, node: Dict[str, Any]) -> CheckpointTuple:
        pending_writes = None
        raw_pw = node.get("pendingWrites")
        if raw_pw:
            decoded: list[tuple[str, str, Any]] = []
            for w in raw_pw:
                if isinstance(w, dict) and "first" in w and "second" in w:
                    # ожидаем формат, который возвращает бек: first=task_id, second=channel, third=typed
                    task_id = w["first"]
                    channel = w["second"]
                    tv = w.get("third")
                    value = self._decode_typed(tv)
                    decoded.append((task_id, channel, value))
                elif isinstance(w, (list, tuple)):
                    try:
                        first, channel, tv = w
                        decoded.append((first, channel, self._decode_typed(tv)))
                    except Exception:  # pragma: no cover
                        continue
            pending_writes = decoded

        return CheckpointTuple(
            config=self._decode_config(node.get("config")),
            checkpoint=self._decode_cp(node["checkpoint"]),
            metadata=self._dec_meta(node.get("metadata")),
            parent_config=self._decode_config(node.get("parentConfig")),
            pending_writes=pending_writes,
        )

    # =================================================================
    # async-методы BaseCheckpointSaver
    # =================================================================
    async def aget_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        cid = get_checkpoint_id(cfg)
        api_cfg = self._to_api_config(cfg)
        tid = api_cfg.get("threadId")

        if cid:
            path = f"/checkpoint/{tid}/{cid}"
            params = {"checkpointNs": api_cfg.get("checkpointNs", "")}
        else:
            path = f"/checkpoint/{tid}"
            params = None

        resp = await self._http("GET", path, params=params)
        logger.debug("AGW aget_tuple response: %s", resp.text)

        if not resp.text or resp.status_code in (404, 406):
            return None
        resp.raise_for_status()
        return self._to_tuple(resp.json())

    async def alist(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        payload = {
            "config": self._to_api_config(cfg) if cfg else None,
            "filter": filter,
            "before": self._to_api_config(before) if before else None,
            "limit": limit,
        }
        resp = await self._http("POST", "/checkpoint/list", json=payload)
        logger.debug("AGW alist response: %s", resp.text)
        resp.raise_for_status()
        for item in resp.json():
            yield self._to_tuple(item)

    async def aput(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        payload = {
            "config": self._to_api_config(cfg),
            "checkpoint": self._encode_cp(cp),
            "metadata": get_checkpoint_metadata(cfg, metadata),
            "newVersions": new_versions,
        }
        resp = await self._http("POST", "/checkpoint", json=payload)
        logger.debug("AGW aput response: %s", resp.text)
        resp.raise_for_status()
        return resp.json()["config"]

    async def aput_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        enc = [{"first": ch, "second": self._encode_typed(v)} for ch, v in writes]
        payload = {
            "config": self._to_api_config(cfg),
            "writes": enc,
            "taskId": task_id,
            "taskPath": task_path,
        }
        resp = await self._http("POST", "/checkpoint/writes", json=payload)
        logger.debug("AGW aput_writes response: %s", resp.text)
        resp.raise_for_status()

    async def adelete_thread(self, thread_id: str) -> None:
        resp = await self._http("DELETE", f"/checkpoint/{thread_id}")
        resp.raise_for_status()

    # =================================================================
    # sync-обёртки
    # =================================================================
    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def list(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        aiter_ = self.alist(cfg, filter=filter, before=before, limit=limit)
        while True:
            try:
                yield self._run(anext(aiter_))
            except StopAsyncIteration:
                break

    def get_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        return self._run(self.aget_tuple(cfg))

    def put(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        return self._run(self.aput(cfg, cp, metadata, new_versions))

    def put_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        self._run(self.aput_writes(cfg, writes, task_id, task_path))

    def delete_thread(self, thread_id: str) -> None:
        self._run(self.adelete_thread(thread_id))

    def get_next_version(self, current: Optional[str], channel: ChannelProtocol) -> str:
        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = random()
        return f"{next_v:032}.{next_h:016}"

    # ------------------------------------------------------------------ #
    # Convenience factory                                                #
    # ------------------------------------------------------------------ #
    @classmethod
    @asynccontextmanager
    async def from_base_url(
        cls,
        base_url: str,
        *,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator["AsyncAGWCheckpointSaver"]:
        saver = cls(base_url, api_key=api_key, **kwargs)
        try:
            yield saver
        finally:
            await saver._client.aclose()
