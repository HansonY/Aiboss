"""全局配置。从 `.env` 读(不存在就全用默认值)。

**这里只有 AI / 向量 / 检索的配置。** 岗位库的路径由 `db/boss_store.py`
自己管(环境变量 `BOSS_DB_PATH`,默认 `data/boss.db`)—— 配置和存储各管各的。

密钥永远只在本机的 `.env` 里(已 gitignore),不进代码、不进日志、不回传页面
(设置接口只回尾四位,见 boss_main 的 /api/boss/settings)。
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── AI ──────────────────────────────────────
    # LLM 供应商/模型由 llm.py 统一解析(LLM_PROVIDER / LLM_MODEL / 各家 key),
    # 这里只留被 llm.py 和 embed.py 直接引用的字段。
    dashscope_api_key: str = ""

    # ── 向量 ────────────────────────────────────
    # 嵌入模型。默认 bge-m3 —— 上游项目四个候选实测下来只有它真能中英互通。
    # 换模型是安全的:向量是派生数据,重建即可;vec_meta 记着模型名,
    # 换了不重建会拒绝检索,不会静默返回垃圾。
    embed_model: str = "BAAI/bge-m3"
    # local = 本机跑(岗位数据不出机器) | dashscope = 云端(需 api key)
    embed_backend: str = "local"

    # ── 检索分档 ────────────────────────────────
    # 相似度两条线:低于 maybe 不返回;之间标「可能相关」并露出分数。
    # 这两个数在上游项目的人工标注上扫过拐点;样本量有限,所以必须可调,
    # 分数一律露给人看,不做静默过滤。
    search_good: float = 0.64
    search_maybe: float = 0.52


settings = Settings()


def reload() -> Settings:
    """设置页写完 `.env` 后重新读一遍,让改动立即生效。"""
    global settings
    settings = Settings()
    return settings
