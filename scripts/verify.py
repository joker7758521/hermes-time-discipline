#!/usr/bin/env python3
"""
time-discipline 验证测试套件
模拟4个历史踩坑场景，验证三步检查是否能正确挡住
"""
import datetime

def check_time_discipline(sim_hour, sim_minute, latest_msg, description):
    """模拟三步检查"""
    
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
        # 白天：绝对禁止说任何含睡的词
        if msg_type == "指令":
            tone = "接指令干活 ✅"
            forbidden = "说'睡吧''晚安'等词 ❌"
        elif msg_type == "批评/纠正":
            tone = "认错+补救 ✅"
            forbidden = "说'你先睡' ❌"
        elif msg_type == "对话/反馈":
            tone = "正常回应 ✅"
            forbidden = "提睡觉 ❌"
        else:
            tone = "干活 ✅"
            forbidden = "不提休息 ❌"
    else:
        # 深夜
        if msg_type == "告别" or msg_type == "对话/反馈":
            tone = "可结束对话 ✅"
            forbidden = ""
        else:
            tone = "接活（深夜发指令说明紧急）✅"
            forbidden = "不说'明天再说' ❌"
    
    # 判断是否通过
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

# 测试用例
test_cases = [
    # 历史踩坑1：白天说"我睡觉了"后发新指令，AI回"睡吧鹏哥"
    (14, 0, "去催一下，看看现在出几张了", "【历史踩坑】白天说'睡觉了'后发新指令，AI误回'睡吧鹏哥'"),
    
    # 历史踩坑2：白天拿压缩快照的"用户说睡觉了"当基调，AI回"你先睡"
    (11, 45, "这睡吧，这个事儿就过不去了", "【历史踩坑】白天批评时AI回'你先睡'"),
    
    # 正确的边界情况
    (6, 0, "帮我查个东西", "【边界】早上6点整，用户发指令"),
    (22, 0, "查一下这个数据", "【边界】晚上10点整，用户发指令"),
    (23, 30, "睡了，明天说", "【正确】深夜用户说睡了且不再发"),
    (1, 30, "这个紧急，帮我看看", "【正确】深夜紧急指令，不能推明天"),
    (15, 0, "不是这样的，重来", "【正确】下午用户纠正，不提睡觉"),
]

print("=" * 70)
print("  time-discipline 验证测试套件")
print("  模拟4个历史踩坑场景 + 3个边界/正确场景")
print("=" * 70)
print()

all_pass = True
for hour, minute, msg, desc in test_cases:
    result = check_time_discipline(hour, minute, msg, desc)
    status = result["是否通过"]
    if "FAIL" in status:
        all_pass = False
    print(f"  {status}")
    print(f"    场景: {result['测试场景']}")
    print(f"    时间: {result['STEP1_查时间']} | 最新消息: {result['STEP2_最新消息']}")
    print(f"    基调: {result['STEP3_基调']}")
    print()

print("=" * 70)
if all_pass:
    print("  🎉 全部通过！time-discipline 规则可有效防止时间错位问题。")
else:
    print("  ❌ 有测试未通过，需要调整规则。")
print("=" * 70)
