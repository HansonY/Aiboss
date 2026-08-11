#!/usr/bin/env bash
# Aiboss —— BOSS 直聘岗位知识库 + AI 匹配。唯一入口:
#
#   ./boss.sh                首次自动装环境,然后起服务 → http://localhost:8001
#
#   ./boss.sh index          给岗位片段建/补向量索引(零网络,本地 bge-m3)
#   ./boss.sh index-status   只看索引现状,不加载模型
#   ./boss.sh find <关键词>   命令行语义检索(全在本地,不需要任何 key)
#   ./boss.sh ask  <问题>     基于岗位库回答,强制带出处(要 LLM key)
#   ./boss.sh llmtest        测当前 AI 配置通不通(配完必跑)
#   ./boss.sh llmsniff       不知道 key 是哪家的?挨个试一遍
#
#   进阶(可选,要 playwright):login / fetch / probe / record / inspect
#
# 数据全在本机:岗位库 data/boss.db、密钥 .env(0600)—— 都已 gitignore。
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-.venv/bin/python}"

# ── 首次运行:自动建环境 ─────────────────────────────────────
# 依赖里有 sentence-transformers(带 torch,几百 MB)—— 语义搜索的向量模型
# 在本机跑、数据不出机器,这是这个项目的立场,所以这份体积省不掉。
if [ ! -x "$PY" ] && [ -z "${PYTHON:-}" ]; then
  echo "首次运行:创建 .venv 并安装依赖(含 torch,几分钟)…"
  # 3.10–3.13(pydantic-core/torch 的稳定区间;3.14 会被启动守卫拦下并给出说明)
  PYBIN=$(command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
  "$PYBIN" -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
  echo "✓ 环境就绪"
fi
[ -x "$PY" ] || { echo "找不到 $PY —— 设 PYTHON=<python路径> 或删掉 .venv 重跑"; exit 1; }

# 独立 db,默认在仓库自己的 data/ 下
export BOSS_DB_PATH="${BOSS_DB_PATH:-data/boss.db}"

case "${1:-web}" in
  snippet)
    # 把控制台片段打出来,方便直接复制
    cat scripts/boss_snippet.js
    echo
    echo "# ↑ 复制以上全部,粘到 zhipin.com 页面的 F12 → Console" >&2
    exit 0 ;;
  llmsniff)
    # key 到底是哪家的?挨个试一遍,不用改 .env 一家家换
    exec "$PY" -c "import sys;sys.path.insert(0,'backend');import llm,json;print(json.dumps(llm.sniff(),ensure_ascii=False,indent=1))" ;;
  llmtest)
    # 配完模型先跑这个 —— 各家端点和模型名改得勤,别等提取时才发现不通
    exec "$PY" -c "import sys;sys.path.insert(0,'backend');import llm,json;print(json.dumps(llm.probe(),ensure_ascii=False,indent=1))" ;;
  login)   exec "$PY" backend/boss_cli.py login ;;
  fetch)   shift; exec "$PY" backend/boss_cli.py fetch "$@" ;;
  whoami)  exec "$PY" backend/boss_cli.py whoami ;;
  probe)   exec "$PY" backend/boss_probe.py ;;
  record)  exec "$PY" backend/boss_record.py ;;
  inspect) exec "$PY" backend/boss_inspect.py ;;
  index)        exec "$PY" scripts/boss_index.py "${@:2}" ;;
  index-status) exec "$PY" scripts/boss_index.py --status ;;
  find)
    shift
    [ $# -gt 0 ] || { echo "用法: ./boss.sh find <关键词>"; exit 1; }
    exec "$PY" - "$@" <<'EOF'
import sys
sys.path.insert(0, "backend")
import kb
from knowledge.boss_space import BOSS_SPACE
r = kb.bind(BOSS_SPACE).search(" ".join(sys.argv[1:]), limit=10)
th = r["thresholds"]
for lbl, key, mark in (("相关", "good", "✓"), ("可能相关", "maybe", "?")):
    if not r[key]:
        continue
    line = th["good"] if key == "good" else th["maybe"]
    print(f"{lbl}({len(r[key])} 条,≥{line}):")
    for it in r[key]:
        flag = "" if it.get("jd_state") == "have" else "  ⚠️没抓到职位描述"
        closed = "  ⚠️已关闭" if it.get("job_state") == "closed" else ""
        print(f"  {mark} {it['score']:.3f}  {(it.get('title') or '?')[:26]:<28}"
              f"{(it.get('company') or '?')[:12]:<14}{it.get('salary') or '':<14}"
              f"{flag}{closed}")
        print(f"        {(it.get('text') or '')[:90]}")
if r["verdict"] == "nothing":
    print(f"库里没有。最接近的分数:{r['nearest_below']}(下限 {th['maybe']})")
elif r["verdict"] == "only_maybe":
    print(f"\n⚠️ 全部落在「可能相关」—— 分档线是在短内容上标出来的,"
          f"\n   岗位 JD 是长段落,同样相关度算出来偏低。分数看得见,自己判断。")
print(f"\n模型 {r['model']}")
EOF
    ;;
  ask)
    shift
    [ $# -gt 0 ] || { echo "用法: ./boss.sh ask <问题>"; exit 1; }
    exec "$PY" - "$@" <<'EOF'
import sys
sys.path.insert(0, "backend")
import kb
from knowledge.boss_space import BOSS_SPACE
r = kb.bind(BOSS_SPACE).ask(" ".join(sys.argv[1:]))
print(r["answer"])
if not r["answered"]:
    print(f"\n({r['reason']};最接近 {r.get('nearest_scores')})")
    sys.exit(0)
print()
for c in r["citations"]:
    print(f"  [{c['n']}] {c.get('company') or '?'} · {(c.get('title') or '')[:30]}"
          f" · {c.get('salary') or ''}  {c.get('url') or ''}")
if r["dropped_bogus_citations"]:
    print(f"\n(剔掉了模型编的编号 {r['dropped_bogus_citations']})")
if r["only_maybe"]:
    print("\n⚠️ 依据全是「可能相关」那一档 —— 别当确定答案。")
EOF
    ;;
  web)
    echo "Aiboss → http://localhost:8001   (库:$BOSS_DB_PATH)"
    echo "开着插件侧边栏浏览 BOSS,岗位自动进库。"
    exec "$PY" -m uvicorn boss_main:app --app-dir backend --port 8001 --reload \
         --reload-dir backend
    ;;
  *) echo "用法: ./boss.sh [web|index|index-status|find|ask|llmtest|llmsniff|login|fetch]"; exit 1 ;;
esac
