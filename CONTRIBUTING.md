# 参与进来

先说清楚:这是个**个人自用**的工具([免责声明](README.md#使用限制与免责声明)),
不追求做成通用产品。欢迎 PR,但请理解取舍。

## 流程

`main` 有保护,直接推不进去 —— 所有改动走 PR:

1. Fork → 建分支(`fix/xxx` 或 `feat/xxx`)
2. 改完**本地跑一遍自检**:
   ```bash
   .venv/bin/python scripts/match_selftest.py    # 91 条口径断言
   .venv/bin/python scripts/kb_invariants.py     # 内核不许认识业务表
   ```
3. 开 PR。CI 会自动跑上面两项 + 编译检查 + 「不许有数据/密钥进仓库」。

## 几条硬规矩(踩了会被要求改)

- **不许把 `data/` 或 `.env` 提上来。** 那是每个人自己的岗位库、简历和 API key。
- **`backend/kb/` 不许认识业务表。** 它只知道 `fragments` 和 `frag_vec`,业务差异从
  `Space` 注入(`knowledge/boss_space.py`)。`kb_invariants.py` 会检查。
- **改了口径就补断言。** `boss_match.py` 那些判定(经验解析、学历序、薪资口径、
  远程优先于城市…)每一条在 `match_selftest.py` 里都有对应断言。
  这类 bug 的表现是「不报错,只是数悄悄错了」,靠断言钉住,不靠记性。
- **别削弱模型输出的校验。** quote 必须能在原文里逐字找到、引不出的丢弃并计数、
  硬门槛 fail 不给「值得投」—— 这三条是这套东西可信的地基。
  想加自己的判断标准,用 `/me.html` 的「自定义匹配 skill」(进 prompt 的 D 段),
  不要去掉校验规则。
- **状态用多态不用布尔。** 「没有」和「还不知道」必须分得开
  (`jd_state` 三态、门槛四态)。混成一个布尔之后,「该去补数据还是该认命」说不清。

## 版本号

**唯一来源是 `extension/manifest.json` 的 `version`**,仓库 tag 跟着它走
(manifest 是 `0.5.0` → tag 就是 `v0.5.0`)。

理由:Chrome 要求扩展版本号**只能递增**,改小了装不上。让它当基准,
两套号就不会打架 —— 反过来让仓库版本当基准的话,迟早要把 manifest 往回改。

发版:先改 manifest 的 version,提交,再 `git tag -a vX.Y.Z && git push origin vX.Y.Z`。

## 提 Issue

比 PR 更受欢迎的一类:**说清一个判断为什么不对**。
带上岗位标题(公司可以涂)、你看到的结论、你认为对的结论 —— 这比「感觉不准」有用得多。

⚠️ **别在 Issue 里贴你的简历原文或完整 JD**,那是你自己的数据。
