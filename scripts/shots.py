#!/usr/bin/env python3
"""给 README 出干净截图 —— **只对着演示库跑,永远不碰你自己的库**。

    BOSS_DB_PATH=data/demo.db .venv/bin/python scripts/demo_db.py   # 先造假数据
    BOSS_DB_PATH=data/demo.db .venv/bin/python -m uvicorn boss_main:app \\
        --app-dir backend --port 8002                                # 起演示服务
    .venv/bin/python scripts/shots.py                                # 截图

需要 playwright(不在主依赖里,截图才用):
    .venv/bin/pip install playwright && .venv/bin/playwright install chromium

**为什么要脚本化。** 拿自己的库手动截图,一定会漏出个人信息 ——
期望城市、工作年限、薪资底线全印在门槛卡上,岗位标题和 JD 又是真公司的。
手动涂麻烦且总会漏(实测第一版涂完还剩薪资底线和一行能定位到公司的 JD)。
对着演示库自动截,出来的图不用涂,而且改了 UI 重跑一条命令就能更新。
"""
from __future__ import annotations

import pathlib
import sys

BASE = "http://localhost:8002"
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "img"

SHOTS = [
    # (文件名, 路径, 视口宽, 视口高, 截图前等多久)
    ("match.png", "/match.html#demo_1", 1440, 940, 2.5),
    ("library.png", "/", 1440, 940, 2.5),
]


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("需要 playwright:\n"
              "  .venv/bin/pip install playwright\n"
              "  .venv/bin/playwright install chromium")
        raise SystemExit(1)

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name, path, w, h, wait in SHOTS:
            pg = b.new_page(viewport={"width": w, "height": h},
                            device_scale_factor=2)   # 2x,README 里缩显也清楚
            pg.goto(BASE + path, wait_until="networkidle")
            pg.wait_for_timeout(int(wait * 1000))
            # 这两页是全高布局(页面本身不滚),所以视口截图就是完整界面
            pg.screenshot(path=str(OUT / name))
            print(f"  ✓ {name}  {w}x{h}@2x")
            pg.close()
        b.close()
    print(f"\n截好了 → {OUT}")
    print("⚠️  确认一遍图里没有真数据再提交(应该全是 星野智能/橙川数据 这类假公司)")


if __name__ == "__main__":
    main()
