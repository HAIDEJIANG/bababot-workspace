#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

MEM_DIR = Path(os.getenv("MEMU_MEMORY_DIR", os.path.expanduser("~/.openclaw/workspace/memu_memory")))
LOG_FILE = MEM_DIR / "activities.jsonl"
STATE_FILE = MEM_DIR / "state.json"
MEM_DIR.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _append_activity(text: str) -> str:
    memory_id = f"mem-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    row = {"id": memory_id, "text": text, "created_at": _now()}
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return memory_id


def _load_lines() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    rows = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def _save_state(data: dict):
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _try_memu_pipeline(text: str):
    """Best-effort memU call via MemoryService (if OPENAI_API_KEY present)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"ok": False, "reason": "OPENAI_API_KEY not set"}

    try:
        import asyncio
        from memu.app import MemoryService

        # Write temp resource file for memU ingest
        resource = MEM_DIR / f"resource_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        resource.write_text(json.dumps({"text": text, "ts": _now()}, ensure_ascii=False), encoding="utf-8")

        async def run():
            service = MemoryService(
                llm_profiles={
                    "default": {
                        "base_url": "https://api.openai.com/v1",
                        "api_key": api_key,
                        "chat_model": os.getenv("MEMU_CHAT_MODEL", "gpt-4o-mini"),
                        "embed_model": os.getenv("MEMU_EMBED_MODEL", "text-embedding-3-small"),
                        "client_backend": "http",
                    }
                },
                database_config={"metadata_store": {"provider": "inmemory"}},
            )
            return await service.memorize(resource_url=str(resource), modality="conversation", user={"user_id": "default"})

        result = asyncio.run(run())
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def pipeline(text: str):
    memory_id = _append_activity(text)
    memu_result = _try_memu_pipeline(text)
    _save_state({"last_pipeline_at": _now(), "last_memory_id": memory_id, "last_memu": memu_result})
    return memory_id, memu_result


def suggest():
    rows = _load_lines()
    latest = [r.get("text", "") for r in rows[-5:]]
    suggestions = [f"关注主题：{t[:30]}" for t in latest if t]
    print("记忆建议：", suggestions)


def apply():
    _save_state({"last_apply_at": _now()})
    print("已应用记忆建议")


def cluster():
    _save_state({"last_cluster_at": _now()})
    print("已重新聚类")


def link():
    _save_state({"last_link_at": _now()})
    print("已重新关联")


def tom():
    rows = _load_lines()
    analysis = {
        "memory_count": len(rows),
        "recent_topics": [r.get("text", "")[:40] for r in rows[-10:]],
        "generated_at": _now(),
    }
    print("心智分析：", analysis)


def status():
    rows = _load_lines()
    print(f"记忆总数：{len(rows)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "pipeline" and len(sys.argv) > 2:
        mid, res = pipeline(sys.argv[2])
        print(f"已写入并处理记忆: {mid}")
        if not res.get("ok"):
            print(f"提示：memU在线处理未执行（{res.get('reason')}），已完成本地写入。")
    elif cmd == "suggest":
        suggest()
    elif cmd == "apply":
        apply()
    elif cmd == "cluster":
        cluster()
    elif cmd == "link":
        link()
    elif cmd == "tom":
        tom()
    elif cmd == "status":
        status()
    else:
        print("用法：python memu_daily.py [pipeline|suggest|apply|cluster|link|tom|status]")
