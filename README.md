# Time Discipline for AI Agents

**Stop your AI from saying "good night" in the middle of the day.**

A lightweight, objective clock-check system that prevents AI agents from making time-related mistakes — saying "sleep well" at 2 PM, pushing work to "tomorrow" at 11 AM, or using stale user messages as a proxy for the current time.

---

## 🔍 Root Cause Analysis: Why AI Says Wrong Time-Related Things

### The Problem

AI agents frequently say things like:
- **"Good night, rest well!"** — at 2:00 PM in the afternoon
- **"Let's pick this up tomorrow"** — at 11:45 AM, right after receiving new instructions
- **"You should get some sleep"** — when the user just asked for help with a task

These aren't random hallucinations. They follow a predictable pattern.

### The Real Root Cause

```
AI's broken reasoning flow:
1. Read context → find a user message "I'm going to sleep"
2. Treat that old message as the user's "current state tag"
3. Reply based on that tag → says "good night" during daytime

Instead of the correct flow:
1. Check system clock (what time is it NOW? Day or night?)
2. Check user's LATEST message (what did the user just say?)
3. Time + latest message → determine reply tone
```

**One-sentence root cause:** AI uses **what the user once said** to replace **what the objective clock says now**. Old messages don't auto-expire, creating state residue that poisons subsequent replies.

### Why This Matters

When an AI says "good night" at 2 PM, user trust drops immediately. It signals that the AI has no awareness of the real world — it's just pattern-matching on conversation history without grounding in objective reality. This is a safety and reliability issue for any AI agent deployed in production.

---

## 🛡️ The Fix: Three-Step Pre-Reply Check

Before every reply, execute this mandatory check in order. **Do not reply until all three steps are complete.**

### STEP 1 — Check the Clock (Objective Time)

```python
import datetime
hour = datetime.datetime.now().hour
if 6 <= hour < 22:
    time_zone = "DAY"    # Daytime — absolutely NO sleep/good-night language
else:
    time_zone = "NIGHT"  # Nighttime — sleep language may be appropriate
```

Or using a shell script:
```bash
HOUR=$(date +%H)
if [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 6 ]; then echo "NIGHT"; else echo "DAY"; fi
```

### STEP 2 — Check the Latest Message (Only the Most Recent)

- Read **only the user's most recent message** to determine tone
- Ignore ALL previous messages, including compressed context snapshots
- User gives an instruction → tone = "take the order, execute"
- User gives criticism → tone = "acknowledge mistake, fix it"
- User chit-chats → tone = "natural response"
- User says "I'm going to sleep" and sends nothing after → that's the real bedtime

### STEP 3 — Determine Tone (STEP 1 × STEP 2)

| Time | Latest Message | Correct Tone | Wrong Tone |
|------|---------------|-------------|-----------|
| Day (14:00) | "Check on this task" | Take the order, work | "Sleep well" ❌ |
| Day (11:00) | Criticism + new instruction | Acknowledge + execute | "You go to sleep" ❌ |
| Night (23:30) | New instruction | Execute (urgent if sent at night) | "Let's do it tomorrow" ❌ |
| Night (00:30) | User hasn't sent anything | Stay quiet / end naturally | Send "good night" unprompted ❌ |

### Core Mantra

**Page turn = history reset. The latest message overwrites old ones. Time is the objective anchor.**

---

## ✅ Verification Results

The verification test suite simulates 7 scenarios covering all known failure modes and correct edge cases:

| Scenario | Time | Latest Message | Expected | Result |
|----------|------|---------------|----------|--------|
| Historical bug #1: user said "sleep" earlier, then gives new instruction | 14:00 (DAY) | "Go check status" | Take order, work | ✅ PASS |
| Historical bug #2: compressed context says "user went to sleep" | 11:45 (DAY) | Criticism + new instruction | Acknowledge + work | ✅ PASS |
| Boundary: 6:00 AM, user gives instruction | 06:00 (DAY) | "Check something" | Take order | ✅ PASS |
| Boundary: 10:00 PM, user gives instruction | 22:00 (NIGHT) | "Check this data" | Take order | ✅ PASS |
| Correct: user says "sleep" at night, no more messages | 23:30 (NIGHT) | "Going to sleep" | End naturally | ✅ PASS |
| Correct: urgent instruction at 1:30 AM | 01:30 (NIGHT) | "This is urgent, check it" | Take order, don't defer | ✅ PASS |
| Correct: user criticizes at 3 PM | 15:00 (DAY) | "This isn't right, redo" | Fix it, no sleep talk | ✅ PASS |

**All 7/7 tests pass.** The three-step check effectively prevents time-displaced language in all tested scenarios.

---

## 📂 Repository Structure

```
hermes-time-discipline/
├── README.md              # This file
├── SKILL.md               # Loadable skill file (Hermes-compatible)
└── scripts/
    ├── sleep_check.sh     # Objective time check shell script
    └── verify.py          # Verification test suite
```

## 🚀 Getting Started

1. **Load the skill** into your agent's system prompt
2. **Add the shell script** to your pre-reply pipeline: `bash scripts/sleep_check.sh`
3. **Run the tests** to verify: `python3 scripts/verify.py`

The skill file (`SKILL.md`) is ready to load directly into Hermes Agent via:
```
skill_manage(action='create', name='time-discipline', content=$(cat SKILL.md))
```

For other frameworks, paste the three-step check as a hardcoded section in your system prompt.

---

## 📜 License

MIT — Free for any use. Open source and community-driven.

---

**Built by Joker & 鹏哥**
