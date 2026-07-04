# Growth Playbook — Tactics, Templates & Metrics

## Table of Contents
1. [Viral Loop Templates](#viral-loop-templates)
2. [Growth Tactics by Stage](#growth-tactics-by-stage)
3. [Metric Benchmarks](#metric-benchmarks)
4. [MVP Validation Checklist](#mvp-validation-checklist)
5. [Platform-Specific Strategies](#platform-specific-strategies)

---

## Viral Loop Templates

### Template 1: Artifact Share Loop (最适合 UGC/创作类产品)

```
User creates artifact (badge, card, image, test result)
  ↓
Artifact is beautiful/funny/identity-expressing → user WANTS to share
  ↓
Artifact contains entry point (QR, link, subtle branding)
  ↓
Friend sees artifact on social media → "I want one too"
  ↓
Friend clicks → creates their own → shares → loop continues
```

**K-factor drivers:**
- Share rate: artifact quality (the better it looks, the more it spreads)
- Conversion rate: clarity of CTA ("scan to make yours")
- Speed: time from click to first artifact (must be <60s)

**Products that use this:** 小年糕, Canva, MBTI tests, Spotify Wrapped

### Template 2: Collaborative Loop (最适合社交/工具类产品)

```
User creates something → needs collaborators
  ↓
Invites friends via link/message
  ↓
Friends join → contribute → invite their friends
  ↓
Group value grows with each member → more invites
```

**K-factor drivers:**
- Invite rate: necessity of collaboration (can I do this alone?)
- Conversion rate: social obligation (friend asked me)
- Retention: group dependency (if I leave, the group suffers)

**Products that use this:** Figma, Notion, 飞书, multi-player games

### Template 3: Challenge Loop (最适合体验/成就类产品)

```
User completes challenge → earns badge/score
  ↓
Challenge result is shareable + competitive
  ↓
Friends see result → "I can beat that" or "I want to try"
  ↓
Friends attempt challenge → share their result → loop continues
```

**K-factor drivers:**
- Share rate: competitiveness + achievement pride
- Conversion rate: "this looks fun" impulse
- Repeat rate: new challenges keep the loop fresh

**Products that use this:** Strava, Wordle, Keep challenges, 咕咚

---

## Growth Tactics by Stage

### Stage 1: Cold Start (0 → 1,000 users)

**Goal:** Validate that strangers want this.

Tactics:
- **Seed on one community** — V2EX, 小红书, Reddit, ProductHunt (pick ONE, go deep)
- **Founder-led sharing** — your own social circle, but with shareable artifacts
- **Content marketing** — write about the problem, not the product
- **Target micro-influencers** — people with 1K-10K followers, not celebrities

**Validation signals:**
- Organic sharing (people share without being asked)
- Return visits (people come back without notification)
- User-created content (people make things you didn't expect)

### Stage 2: Growth (1K → 100K users)

**Goal:** Optimize the viral loop.

Tactics:
- **A/B test the share artifact** — small changes in design = big changes in share rate
- **Reduce friction** — every extra click in the flow costs 50% of users
- **Add social proof** — "12,345 people have already made theirs"
- **Seasonal themes** — 春节版, 毕业季, 年终总结 (cultural moments)
- **Referral rewards** — invite 3 friends, unlock premium style

**Key optimization:**
```
Conversion funnel: View → Click → Create → Share
Measure each step. Fix the worst step first.
```

### Stage 3: Retention (100K → 1M+ users)

**Goal:** Build the moat.

Tactics:
- **Sunk cost mechanics** — history, collections, annual reports
- **Social bonds** — friends, followers, communities
- **Content depth** — more styles, more features, power user tools
- **Habit formation** — daily/weekly triggers, streak rewards
- **Premium tier** — free keeps growing, paid keeps the lights on

---

## Metric Benchmarks

### Consumer Product Health Metrics

| Metric | Good | Great | World-class |
|--------|------|-------|-------------|
| D1 Retention | 30% | 40% | 50%+ |
| D7 Retention | 15% | 25% | 35%+ |
| D30 Retention | 5% | 10% | 20%+ |
| Share rate | 10% | 25% | 40%+ |
| Viral coefficient (K) | 0.5 | 1.0 | 1.5+ |
| Time to first value | <3 min | <1 min | <30s |

### Viral Loop Benchmarks

| Metric | Fail | Pass | Excellent |
|--------|------|------|-----------|
| Click-through on shared artifact | <2% | 5% | 10%+ |
| Conversion from click to create | <5% | 15% | 30%+ |
| Time from landing to first creation | >5 min | 2 min | <60s |
| % who share after first creation | <10% | 25% | 50%+ |

---

## MVP Validation Checklist

### Before writing any code:

```
□ Can you describe the product in one sentence?
□ Can you name the primary human weakness it exploits?
□ Does the core loop involve ≥3 of the 7 levers?
□ Is there a natural share trigger in the core experience?
□ Can a first-time user reach "aha" in <60 seconds?
□ Can you mock up the share artifact? (Figma, Canva, even hand-drawn)
□ Would YOU share that artifact on your social media?
□ Can you build and ship the MVP in <1 week?
□ Is there a specific community you'll launch to?
□ Do you have a clear "this worked" metric for week 1?
```

**If ≥3 answers are "no", rethink before building.**

### The Template Test:

Before building a product, create the share artifact as a static template.
Share it manually. See if people ask "how did you make this?"

If the template doesn't spread → the product won't either.

---

## Platform-Specific Strategies

### 微信生态 (WeChat)

- **Best format:** 小程序 (zero download, native share cards)
- **Share mechanic:** 朋友圈 card + 群聊 card (different formats)
- **Growth hack:** "长按识别二维码" on shared images
- **Key metric:** 次日留存 (next-day retention, not DAU)

### 小红书 (Xiaohongshu)

- **Best format:** 高颜值图片 + 故事化文案
- **Content strategy:** Not "use my product" but "look at this cool thing I made"
- **Growth hack:** 热门标签 + 教程型内容 ("3步做出超酷的XX")
- **Key metric:** 收藏率 (save rate, not likes)

### Twitter/X

- **Best format:** Thread with visuals, "build in public"
- **Share mechanic:** Retweets + quote tweets
- **Growth hack:** Controversial takes + product demos
- **Key metric:** Quote tweet rate (not impressions)

### Product Hunt / V2EX

- **Best format:** "I built this in a weekend" + demo
- **Launch strategy:** First-day engagement determines ranking
- **Growth hack:** Respond to every comment, ship fixes in real-time
- **Key metric:** Upvotes in first 4 hours
