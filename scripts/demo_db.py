#!/usr/bin/env python3
"""造一个**全假数据**的演示库,用来截图和录屏。

    BOSS_DB_PATH=data/demo.db .venv/bin/python scripts/demo_db.py
    BOSS_DB_PATH=data/demo.db ./boss.sh          # 起服务,截图去

**为什么需要它。** 直接拿自己的库截图,一定会漏出个人信息:期望城市、工作年限、
薪资底线全在门槛卡上,岗位标题和 JD 又是真公司的。手动涂很烦而且总会漏一处
(实测第一版涂完还剩薪资底线和一行能定位到公司的 JD)。造一份假的一次性解决:
截出来的图不需要任何涂抹,也能放心公开。

公司名和 JD 全是编的;简历是一份合成的样例。`data/` 已 gitignore,
所以 demo.db 不会进仓库。
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "backend"))

from db import boss_store as bs                       # noqa: E402
from knowledge import boss_fragments as bfr           # noqa: E402

RESUME = """姓名:示例(这是合成的样例简历,不是任何真人)
求职意向:iOS / 全栈开发工程师 · 期望城市 上海 · 期望薪资 25-35K
学历:本科,计算机科学与技术

工作经历
2019.03 - 2023.08  云岚科技  iOS 开发工程师
  · 独立负责一款日活 20 万的记账 App 的 iOS 端,从 0 到上线
  · 用 Swift + SwiftUI 重写原有 Objective-C 首页,启动耗时 1.8s → 0.8s
  · 接 AVFoundation 做语音记账的录音与降噪,处理过内存峰值
2023.09 - 至今  墨行网络  全栈工程师
  · 前端 React + TypeScript,后端 Node.js + PostgreSQL,Docker 部署
  · 用 Python 接 OpenAI 兼容接口做了个内部知识问答(RAG)

技能:Swift、SwiftUI、Objective-C、AVFoundation、React、TypeScript、
Node.js、PostgreSQL、Docker、Python、Git

其他:不接受长期出差;可以偶尔加班,不接受大小周。
"""

JOBS = [
    dict(job_id="demo_1", title="高级 iOS 开发工程师", company="星野智能",
         city="上海", district="静安区", salary_text="30-50K·14薪",
         salary_min=30, salary_max=50, salary_months=14,
         experience="3-5年", degree="本科", work_mode="hybrid",
         domain="冥想睡眠App", stack=["iOS", "Swift", "音频"],
         sell="14薪+每周两天远程",
         tags=["Swift", "SwiftUI", "AVFoundation", "性能优化", "组件化"],
         jd="""职位描述
岗位职责:
1. 负责冥想与睡眠 App 的 iOS 端开发,以 Swift / SwiftUI 为主;
2. 负责音频播放链路(后台播放、AirPlay、混音)与性能优化;
3. 参与从需求到上线的完整迭代,直接对结果负责。
任职要求:
1. 3 年以上 iOS 开发经验,精通 Swift,能读 Objective-C 旧代码;
2. 熟悉 AVFoundation 或 AVAudioEngine,做过音频/视频相关功能;
3. 有启动耗时、内存优化等性能调优实战经验;
4. 加分:有 React Native 或全栈经验;有独立开发且上线经验。
福利:14 薪、每周两天远程、Mac 顶配。"""),
    dict(job_id="demo_2", title="AI 应用全栈工程师(全职远程)", company="橙川数据",
         city="杭州", salary_text="25-40K", salary_min=25, salary_max=40,
         experience="3-5年", degree="本科", work_mode="remote",
         domain="AI客服工具", stack=["全栈", "LLM应用", "React"],
         sell="全职远程不限城市",
         tags=["React", "TypeScript", "Node.js", "PostgreSQL", "LLM", "RAG"],
         jd="""职位描述
我们在做一款面向中小商家的 AI 客服工具,团队 8 人,全职远程、不限城市。
岗位职责:
1. 前端 React + TypeScript,后端 Node.js,负责端到端交付;
2. 接入大模型能力(检索增强、意图识别),把效果调到能上线;
3. 和产品一起定方案,不做纯执行。
任职要求:
1. 3 年以上全栈经验,前后端都能独立完成;
2. 做过 LLM 应用落地(RAG / Agent 皆可),知道效果差在哪、怎么调;
3. 能适应远程协作,自己推进事情。"""),
    dict(job_id="demo_3", title="资深 Android 开发工程师", company="深蓝声学",
         city="深圳", district="南山区", salary_text="35-55K·15薪",
         salary_min=35, salary_max=55, salary_months=15,
         experience="5-10年", degree="本科", work_mode="onsite",
         domain="智能音箱", stack=["Android", "音视频", "C++"],
         sell="硬件+软件全链路",
         tags=["Kotlin", "Android", "C++", "音频算法", "JNI"],
         jd="""职位描述
岗位职责:
1. 负责智能音箱 Android 端系统层与应用层开发;
2. 音频链路调优,与算法团队配合做降噪、回声消除的端侧集成;
3. 通过 JNI 对接 C++ 音频算法库。
任职要求:
1. 5 年以上 Android 经验,精通 Kotlin/Java;
2. 有音频或音视频方向的实战经验;
3. 熟悉 C++ 与 JNI;有嵌入式协作经验加分。
工作地点:深圳南山,现场办公。"""),
    dict(job_id="demo_4", title="前端工程师(数据可视化)", company="云图信息",
         city="上海", district="浦东新区", salary_text="18-28K",
         salary_min=18, salary_max=28, experience="1-3年", degree="本科",
         work_mode="onsite", domain="BI报表", stack=["前端", "可视化"],
         sell="业务稳定",
         tags=["Vue", "ECharts", "TypeScript"],
         jd="""职位描述
岗位职责:负责 BI 报表平台前端开发,图表组件封装与性能优化。
任职要求:1. 1-3 年前端经验,熟悉 Vue 3 + TypeScript;
2. 用过 ECharts 或 D3 做过复杂图表;3. 有大数据量表格渲染优化经验加分。"""),
    dict(job_id="demo_5", title="iOS 开发工程师", company="拾光科技",
         city="上海", salary_text="20-30K·13薪", salary_min=20, salary_max=30,
         salary_months=13, experience="经验不限", degree="大专",
         work_mode="onsite", domain="社区电商", stack=["iOS", "Swift"],
         sell="团队年轻", tags=["Swift", "UIKit", "网络请求"],
         jd="""职位描述
负责社区电商 App 的 iOS 端日常迭代与线上问题修复。
要求:熟悉 Swift 与 UIKit,了解常见网络与缓存方案;有完整上线经验优先。"""),
]


def main() -> None:
    db = bs.db_file()
    if "demo" not in db.name:
        print(f"⚠️  当前 BOSS_DB_PATH 是 {db} —— 这不像演示库,拒绝写入。\n"
              f"   请用:BOSS_DB_PATH=data/demo.db {sys.argv[0]}")
        raise SystemExit(1)

    bs.init_db()
    rows = []
    for j in JOBS:
        d = dict(j)
        d["jd_state"] = bs.JD_HAVE
        d["job_state"] = bs.JOB_OPEN
        d["url"] = f"https://example.com/job/{d['job_id']}"
        d["raw"] = {"demo": True}
        rows.append(d)
    bs.upsert_jobs(rows)
    for j in JOBS:
        bs.save_fragments(j["job_id"], bfr.build(bs.get_job(j["job_id"]) or {}))

    bs.set_me(resume_raw=RESUME, replace_raw=True,
              parsed_by="demo/synthetic",
              parsed_json=json.dumps({"demo": True}, ensure_ascii=False),
              years_exp=6.4, degree="本科", cities=["上海"],
              salary_floor=25, salary_want=35,
              skills=["swift", "swiftui", "objectivec", "avfoundation", "react",
                      "typescript", "nodejs", "postgresql", "docker", "python", "git"])
    print(f"✓ 演示库就绪:{db}")
    print(f"  {len(JOBS)} 个假岗位 + 一份合成简历(6.4 年 / 本科 / 上海 / 底线 25K)")
    print(f"\n起服务截图:BOSS_DB_PATH={db.name and 'data/' + db.name} ./boss.sh")
    print("  匹配分要点一下「AI 分析匹配」才有(会花一次调用)")


if __name__ == "__main__":
    main()
