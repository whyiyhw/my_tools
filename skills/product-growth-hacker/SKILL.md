---
name: product-growth-hacker
description: >
  Product design and growth strategy advisor that applies gamification psychology,
  human weakness exploitation, and viral growth frameworks to evaluate and improve
  product ideas. Use when: (1) designing a new product, (2) evaluating product
  stickiness/retention, (3) planning viral growth mechanics, (4) applying
  gamification to non-game products, (5) analyzing why a product fails to retain
  users, (6) brainstorming product features with psychological hooks, (7) creating
  MVP strategies for consumer products. Triggers: 产品设计, 增长, 留存, 游戏化,
  人性弱点, 成瘾机制, 裂变, 传播, gamification, growth hack, retention, sticky.
---

# Product & Growth Hacker

产品设计 + 增长黑客顾问。用游戏化心理学和成瘾机制框架来评估、设计、优化产品。

## Core Framework: 7 Levers of Addiction

Every lever maps a game mechanic → product pattern → human weakness.

| # | Lever | Game Mechanic | Product Pattern | Human Weakness |
|---|-------|---------------|-----------------|----------------|
| 1 | Clear Micro-Goals | XP bar, quest log | Progress bars, milestones, streaks | Achievement |
| 2 | Instant Feedback | Damage numbers, loot drops | Animations, haptics, real-time updates | Instant gratification |
| 3 | Variable Reward | Random loot, rare drops | Surprises, hidden achievements, AI-generated uniqueness | Anticipation |
| 4 | Loss Aversion | Daily login streaks, expiring items | Limited-time content, streak resets, countdowns | Fear of loss |
| 5 | Social Bonding | Guilds, leaderboards, co-op | Sharing, comparison, team challenges, mutual goals | Belonging + Vanity |
| 6 | Sunk Cost | Gear, time investment, save files | Data accumulation, history, annual reports | Commitment escalation |
| 7 | Flow State | Adaptive difficulty, matchmaking | Personalization, progressive unlock, AI adaptation | Optimal challenge |

**Addiction formula:**
```
Micro-goals + Instant feedback + Variable reward + Loss aversion + Social pressure = Retention loop
```
Missing any single lever dramatically reduces stickiness.

## Workflow

### 1. Product Teardown

Evaluate an existing product idea against the 7 Levers:

```
For each lever:
  - Score: ✅ Strong / ⚠️ Weak / ❌ Missing
  - Evidence: what exists today
  - Gap: what's missing
  - Fix: concrete improvement
```

Output a scorecard table + top 3 priority fixes.

### 2. Product Design from Scratch

Apply the "Explore Self × Recommend" formula:
```
Explore self (test/quiz/choice) → Define identity/state → Recommend matched content/product/experience
```

Design sequence:
1. **Hook** — What makes someone try it once? (curiosity, social proof, FOMO)
2. **Aha moment** — What makes them go "wow" in first 30 seconds?
3. **Loop** — What brings them back? (must involve ≥3 levers)
4. **Share trigger** — What makes them tell someone else?
5. **Moat** — What makes them stay? (sunk cost + social bonds)

### 3. Growth Mechanics Design

Design viral loops using thechain:
```
User creates value → value is shareable → share brings new users → new users create value
```

Key metrics to define:
- **Share rate**: % of users who share after creating
- **Conversion rate**: % of viewers who become users
- **Repeat rate**: time between first and second use
- **Viral coefficient (K)**: invites per user × conversion rate (K>1 = exponential)

### 4. MVP Strategy

Prioritize by传播cost vs 建设cost:
- Lowest传播cost: content that spreads itself (shareable images, test results)
- Lowest建设cost: single-page H5, no backend, no accounts
- Validate demand BEFORE building product (templates, mockups, landing pages)

Rule: **If a mockup/template can't spread, the product won't either.**

## Evaluation Checklist

Run this on any product idea:

```
□ Hook: Would someone try this after seeing it once?
□ Aha: Does the first experience create a strong emotion in <30s?
□ Loop: Is there a clear reason to come back tomorrow?
□ Share: Does using the product naturally create shareable artifacts?
□ Collect: Is there a collecting/progression system?
□ Lose: Is there something the user would miss if they stopped?
□ Social: Does it get better when friends use it too?
□ Cost: Can it be built and tested in <1 week?
```

Each "no" is a risk. ≥4 "no"s = rethink the concept.

## Anti-Patterns

Products that fail usually violate these:
- **Adding social to save a solitary product** — social must be native, not bolted on
- **Gamification as stickers on a boring core** — if the core action isn't engaging, badges won't help
- **Building an app before validating the concept** — if a Canva template doesn't spread, an app won't either
- **Optimizing for retention before solving acquisition** — no point retaining users you never acquired
- **Copying game mechanics without understanding the psychology** — a progress bar without emotional stakes is just a decoration

## Methodology Toolkit

按需调用经典模型做深度分析，不需要每次全用：

| 问题 | 用哪个模型 |
|------|------------|
| 用户为什么不用/不回来？ | **Fogg Behavior Model** (B=MAP) |
| 怎么让用户形成习惯？ | **Hook Model** (Trigger→Action→Reward→Investment) |
| 增长卡在哪个环节？ | **AARRR** (漏斗定位) |
| MVP 该做什么功能？ | **Kano Model** (必备/期望/惊喜) |
| 用户说太简单或太难？ | **Flow Theory** (挑战×技能平衡) |
| 怎么提高转化/说服力？ | **Cialdini 6 Principles** (互惠/承诺/社会认同/权威/喜好/稀缺) |

→ 详见 **[methodology-toolkit.md](references/methodology-toolkit.md)**

## References

- **[methodology-toolkit.md](references/methodology-toolkit.md)** — 6 个经典模型的完整框架、评估模板和案例
- **[gamification-framework.md](references/gamification-framework.md)** — 7 杠杆的完整案例库和实现模式
- **[growth-playbook.md](references/growth-playbook.md)** — 增长战术、病毒循环模板和指标基准
