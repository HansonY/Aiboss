# 目录结构

```
boss.sh              唯一入口:起服务、建索引、命令行检索
requirements.txt     依赖清单(boss.sh 首次自动装)
extension/           Chrome 插件(未打包加载)
  manifest.json      入口声明
  sidepanel.{html,js} 侧边栏:当前岗位门槛核对 + AI 匹配 + 抓取开关
  background.js      service worker:自动存、批量抓、自动翻页
  bridge.js          注入页面:盯内容变化(左右分栏 URL 不变也能发现)
backend/
  boss_main.py       所有 HTTP 接口
  boss_extract.py    页面原文 → 结构化 + 归纳特征(work_mode/domain/stack/sell)
  boss_match.py      机械核对:城市/经验/学历/薪资(四态,不是布尔)
  boss_matchai.py    模型匹配 + quote 逐字校验(引不出原文的丢弃并计数)
  boss_resume.py     简历原文 → 结构化
  llm.py             多供应商 OpenAI 兼容层 + 快档模型 + 耗时统计
  kb/                向量内核(业务无关:片段 → 向量 → 检索 → 问答)
  knowledge/         本项目的适配层(boss_space / boss_fragments / embed)
  db/                SQLite 存取 + schema
  static_boss/       三个页面:岗位库 / 我的简历 / 岗位匹配
scripts/
  boss_index.py      建/补向量索引(独立进程,不占 web 进程内存)
  match_selftest.py  口径自检(零网络零模型,84 条断言)
  kb_invariants.py   守「内核不认识业务表」这条不变量
data/                你的库:boss.db · 待提取队列 · 简历(已 gitignore)
```

## 几个关键约定

- **`kb/` 不许认识业务表。** 它只知道 `fragments` 和 `frag_vec`,业务差异全从
  `Space`(见 `knowledge/boss_space.py`)注入。`scripts/kb_invariants.py` 会检查这条。
- **状态用多态不用布尔。** `jd_state` 是 have/none/unknown,门槛是
  pass/fail/unknown/na —— 「没有」和「还不知道」必须分得开。
- **原文压缩存全量。** `jobs.raw_z` 留整份原始提取结果;简历原文永不覆盖。
- **改口径要跑自检**:`.venv/bin/python scripts/match_selftest.py`。
