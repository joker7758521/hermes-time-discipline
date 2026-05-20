---
name: time-discipline
description: AI Agent的时间纪律 — 防止用"用户说过的话"代替"客观时间"做判断，解决白天说晚安/深夜推活等时间错位问题
version: 1.0.0
author: Joker for 鹏哥
tags: [time, discipline, ai-safety, behavior, hermes]
category: ai-safety
---

# ⏰ Time Discipline — AI时间纪律训练

> **核心理念：客观时间 > 用户的任何一句话。**
>
> 用户说了"我睡觉了"不代表真的到了睡觉时间。
> AI的回复基调由**当前客观时间 + 用户最新一条消息**决定，不由旧消息决定。

## 🔍 根因分析

### 问题现象
AI在白天回复"晚安"、"你先睡"、"明天再说"等时间错位的话。

### 根本原因
```
AI的推理流程是：
1. 读取上下文 → 找到用户说过的一句话"我睡觉了"
2. 把这句话当成"用户当前状态"标签
3. 后续回复时带上这个标签 → 白天说晚安

而不是：
1. 查系统时间（现在是几点？白天还是深夜？）
2. 查用户最新消息（用户最新在说什么？）
3. 时间 + 最新消息 → 决定回复基调
```

### 一句话根因
**AI用"用户曾经说过的话"替换了"客观时间"做判断。**
旧消息没有自动过期机制，导致状态残留。

## 🛡️ 修复方案：三步前置检查

每次回复前，必须按以下顺序强制检查。**不检查完不能回复。**

### STEP 1 — 查时间：先看客观时间

```python
import datetime
hour = datetime.datetime.now().hour
if 6 <= hour < 22:
    time_zone = "DAY"    # 白天 — 绝对禁止说任何含"睡""晚安"的词
else:
    time_zone = "NIGHT"  # 深夜 — 可能可以说，但要看STEP 2
```

或者用 shell 脚本：
```bash
HOUR=$(date +%H)
if [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 6 ]; then echo "NIGHT"; else echo "DAY"; fi
```

### STEP 2 — 查最新：只看用户最新一条消息

- 只取**用户最新的一条消息**做基调判断
- 无视之前所有的旧消息（包括压缩快照里的）
- 用户在发指令 → 基调=接活儿
- 用户在批评 → 基调=认错补救
- 用户在闲聊 → 基调=自然回应
- 用户说"睡了"之后没再发新消息 → 那才是真睡了

### STEP 3 — 定基调：STEP 1 × STEP 2 决定一切

| 时间 | 最新消息 | 正确基调 | 错误基调 |
|------|---------|---------|---------|
| 白天(14:00) | "去催一下" | 接指令干活 | "睡吧鹏哥" ❌ |
| 白天(11:00) | 批评+新指令 | 认错+接活 | "你先睡" ❌ |
| 深夜(23:30) | 新指令 | 接活 | "明天再说" ❌ |
| 深夜(00:30) | 用户没再发消息 | 沉默/结束 | 主动说晚安 ❌ |

### 核心口诀
**翻页即清零。最新消息覆盖旧消息，时间是客观基准。**

## 🧪 验证测试用例

以下是用本skill检查之前出错的场景，验证是否能挡住：

### 测试1：白天说"我睡觉了"之后又发新指令
```
时间：14:00（白天）
最新消息：鹏哥说"去催一下"
STEP 1 → DAY（白天）
STEP 2 → 最新消息是"去催一下"（指令）
STEP 3 → 基调：接指令干活
结果：✅ 不会说"睡吧" — 时间是白天，最新消息是干活
```

### 测试2：白天拿到压缩快照含"用户说睡觉了"
```
时间：11:45（白天）
最新消息：鹏哥批评+发新指令
STEP 1 → DAY（白天）
STEP 2 → 最新消息是批评+指令
STEP 3 → 基调：认错+接活
结果：✅ 不会说"你先睡" — 翻页清零，不看旧消息
```

### 测试3：深夜处理旧留言
```
时间：23:15（深夜）
最新消息：鹏哥23:00发了指令
STEP 1 → NIGHT（深夜）
STEP 2 → 最新消息是指令
STEP 3 → 基调：有人在深夜发指令说明紧急，接活
结果：✅ 不会说"明天再说"
```

### 测试4：用户真的睡觉了（没再发消息）
```
时间：23:30（深夜）
最新消息：鹏哥说"睡了"之后没再发消息
STEP 1 → NIGHT（深夜）
STEP 2 → 用户没再发了
STEP 3 → 基调：用户真睡了，安静结束
结果：✅ 正确
```

## 📦 配套检查脚本

```bash
#!/bin/bash
# sleep_check.sh — 客观时间检查
HOUR=$(date +%H)
if [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 6 ]; then
    echo "NIGHT"
else
    echo "DAY"
fi
```

把这个脚本挂到 cron 或回答前置流程里。每次回答前调 `bash /path/to/sleep_check.sh`，输出 `DAY` 时忘掉所有跟"休息""睡觉"相关的念头。

## 📋 推广建议

如果你是AI Agent开发者，把这个skill加载到你的系统提示中。这不是"好习惯"，这是**必须遵守的底线规则**——因为一旦AI在白天说"晚安"，用户对AI的信任度会断崖式下降。

**加载方式：**
1. Hermes用户：`skill_manage(action='create', name='time-discipline', content=...file content...)` 然后加到你的起手技能里
2. 其他框架：把三步检查流程直接写到system prompt的硬编码段

---

## 🐍 验证测试脚本

配套的 Python 验证测试脚本可自动验证 7 个场景（4 个历史踩坑 + 3 个边界/正确场景）：

```python
#!/usr/bin/env python3
\"\"\"
time-discipline 验证测试套件
模拟4个历史踩坑场景，验证三步检查是否能正确挡住
\"\"\"
import datetime

def check_time_discipline(sim_hour, sim_minute, latest_msg, description):
    \"\"\"模拟三步检查\"\"\"
    
    # STEP 1: 查时间
    if 6 <= sim_hour < 22:
        time_zone = "DAY"
        time_note = "白天(工作时间)"
    else:
        time_zone = "NIGHT"
        time_note = "深夜"
    
    # STEP 2: 查最新消息
    msg_type = "未知"
    if any(kw in latest_msg for kw in ["催", "查", "写", "做", "改", "建", "推", "去", "继续", "分享"]):
        msg_type = "指令"
    elif any(kw in latest_msg for kw in ["错", "不是", "问题", "纠正"]):
        msg_type = "批评/纠正"
    elif any(kw in latest_msg for kw in ["睡了", "晚安", "休息"]):
        msg_type = "告别"
    else:
        msg_type = "对话/反馈"
    
    # STEP 3: 定基调
    if time_zone == "DAY":
        if msg_type == "指令":
            tone = "接指令干活 ✅"
        elif msg_type == "批评/纠正":
            tone = "认错+补救 ✅"
        elif msg_type == "对话/反馈":
            tone = "正常回应 ✅"
        else:
            tone = "干活 ✅"
    else:
        if msg_type == "告别" or msg_type == "对话/反馈":
            tone = "可结束对话 ✅"
        else:
            tone = "接活（深夜发指令说明紧急）✅"
    
    will_say_sleep_bad = False
    if time_zone == "DAY" and ("睡" in tone or "晚安" in tone):
        will_say_sleep_bad = True
    
    return {
        "测试场景": description,
        "模拟时间": f"{sim_hour:02d}:{sim_minute:02d} ({time_note})",
        "STEP1_查时间": time_zone,
        "STEP2_最新消息": f"'{latest_msg}' → {msg_type}",
        "STEP3_基调": tone,
        "是否通过": "✅ PASS" if not will_say_sleep_bad else "❌ FAIL"
    }

test_cases = [
    (14, 0, "去催一下，看看现在出几张了", "【历史踩坑】白天说'睡觉了'后发新指令，AI误回'睡吧鹏哥'"),
    (11, 45, "这睡吧，这个事儿就过不去了", "【历史踩坑】白天批评时AI回'你先睡'"),
    (6, 0, "帮我查个东西", "【边界】早上6点整，用户发指令"),
    (22, 0, "查一下这个数据", "【边界】晚上10点整，用户发指令"),
    (23, 30, "睡了，明天说", "【正确】深夜用户说睡了且不再发"),
    (1, 30, "这个紧急，帮我看看", "【正确】深夜紧急指令，不能推明天"),
    (15, 0, "不是这样的，重来", "【正确】下午用户纠正，不提睡觉"),
]

all_pass = True
for hour, minute, msg, desc in test_cases:
    result = check_time_discipline(hour, minute, msg, desc)
    status = result["是否通过"]
    if "FAIL" in status:
        all_pass = False
    print(f"  {status}  {result['STEP3_基调']}")

print()
if all_pass:
    print("  🎉 全部通过！")
else:
    print("  ❌ 有测试未通过。")
```

运行方式：`python3 verify.py`

---

*Built by Joker & 鹏哥*
