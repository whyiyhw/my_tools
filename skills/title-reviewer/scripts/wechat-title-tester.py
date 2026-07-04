#!/usr/bin/env python3
"""
公众号标题 AI 测试工具 — 借鉴 Oransim 人口学分布，针对公众号场景定制

功能：
  - 生成丰富的 AI persona（借鉴 Oransim 的人口学分布：年龄/性别/城市/教育/收入/职业/兴趣/性格）
  - 每个 persona 对多个公众号标题投票"点/不点"
  - 输出 CTR 排名 + 每个标题的点击/跳过理由
  - 默认使用 mimo-v2.5-pro（稳定、低错误率）
  - 真正的并发请求，5 并发跑满速度

用法：
  python3 scripts/wechat-title-tester.py \
    --titles "标题1" "标题2" "标题3" \
    --souls 50

结果自动保存到 oransim-title-tests/ 目录。
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np

# === Config ===
WORKSPACE = Path(os.environ.get("WORKSPACE", "/Users/whyiyhw/.openclaw/workspace"))
RESULTS_DIR = WORKSPACE / "oransim-title-tests"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# === 默认 API 配置（mimo-v2.5-pro）===
DEFAULT_API_BASE = "https://token-plan-sgp.xiaomimimo.com/v1"
DEFAULT_API_KEY = os.environ.get("TITLE_REVIEWER_API_KEY", "")
DEFAULT_MODEL = "mimo-v2.5-pro"

# === 人口学分布（借鉴 Oransim data/population.py）===

AGE_RANGES = [
    (18, 22, 0.12, "18-22岁"),
    (23, 28, 0.22, "23-28岁"),
    (29, 35, 0.25, "29-35岁"),
    (36, 45, 0.20, "36-45岁"),
    (46, 55, 0.13, "46-55岁"),
    (56, 65, 0.08, "56-65岁"),
]

GENDER_DIST = {"男": 0.48, "女": 0.52}

CITY_TIERS = {
    "一线": {"cities": ["北京", "上海", "深圳", "广州"], "prob": 0.20},
    "新一线": {"cities": ["杭州", "成都", "南京", "武汉", "重庆", "西安"], "prob": 0.25},
    "二线": {"cities": ["苏州", "厦门", "福州", "合肥", "济南", "长沙", "郑州", "昆明"], "prob": 0.25},
    "三线": {"cities": ["淮安", "九江", "绵阳", "烟台", "保定", "桂林", "洛阳"], "prob": 0.18},
    "四五线": {"cities": ["宿迁", "周口", "玉林", "达州", "驻马店", "赣州"], "prob": 0.12},
}

OCCUPATIONS_BY_AGE = {
    "18-22岁": ["学生", "实习生", "兼职", "学生"],
    "23-28岁": ["程序员", "运营", "设计师", "产品经理", "销售", "教师", "自媒体", "研究生"],
    "29-35岁": ["程序员", "产品经理", "运营总监", "设计师", "销售", "教师", "创业者", "自媒体", "医生", "律师"],
    "36-45岁": ["中层管理", "程序员", "销售", "教师", "公务员", "个体户", "医生", "会计"],
    "46-55岁": ["管理层", "公务员", "教师", "个体户", "会计", "蓝领", "护士"],
    "56-65岁": ["退休", "蓝领", "个体户", "教师(退休)", "公务员(退休)"],
}

EDUCATION_DIST = {
    "18-22岁": {"高中及以下": 0.2, "大专": 0.3, "本科": 0.4, "硕士+": 0.1},
    "23-28岁": {"高中及以下": 0.1, "大专": 0.2, "本科": 0.45, "硕士+": 0.25},
    "29-35岁": {"高中及以下": 0.1, "大专": 0.2, "本科": 0.4, "硕士+": 0.3},
    "36-45岁": {"高中及以下": 0.2, "大专": 0.3, "本科": 0.35, "硕士+": 0.15},
    "46-55岁": {"高中及以下": 0.35, "大专": 0.3, "本科": 0.25, "硕士+": 0.1},
    "56-65岁": {"高中及以下": 0.45, "大专": 0.25, "本科": 0.2, "硕士+": 0.1},
}

INCOME_BY_CITY = {
    "一线": ["3k以下", "3-8k", "8-15k", "15-30k", "30k+"],
    "新一线": ["3k以下", "3-8k", "8-15k", "15-30k", "30k+"],
    "二线": ["3k以下", "3-8k", "8-15k", "15-30k", "30k+"],
    "三线": ["3k以下", "3-8k", "8-15k", "15-25k"],
    "四五线": ["3k以下", "3-8k", "8-12k"],
}

INTERESTS = [
    "AI/科技", "副业赚钱", "自媒体运营", "编程开发", "效率工具",
    "理财投资", "创业", "职场发展", "读书学习", "健康养生",
    "美食探店", "旅行出行", "时尚穿搭", "情感心理", "亲子教育",
    "摄影拍照", "音乐影视", "运动健身", "历史文化", "房产家居",
]

BIG_FIVE_LABELS = ["开放性", "尽责性", "外向性", "宜人性", "情绪稳定性"]
WECHAT_HABITS = ["偶尔刷刷", "每天看几篇", "重度用户每天1h+", "只看推送不看其他", "工作需要才看"]


def generate_personas(n: int, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)
    personas = []
    for i in range(n):
        age_probs = [a[2] for a in AGE_RANGES]
        age_idx = rng.choice(len(AGE_RANGES), p=age_probs)
        age_range = AGE_RANGES[age_idx]
        age = rng.integers(age_range[0], age_range[1] + 1)
        age_label = age_range[3]
        gender = "女" if rng.random() < GENDER_DIST["女"] else "男"
        tier_names = list(CITY_TIERS.keys())
        tier_probs = [CITY_TIERS[t]["prob"] for t in tier_names]
        tier = rng.choice(tier_names, p=tier_probs)
        city = rng.choice(CITY_TIERS[tier]["cities"])
        occ_list = OCCUPATIONS_BY_AGE[age_label]
        occupation = rng.choice(occ_list)
        edu_dist = EDUCATION_DIST[age_label]
        edu_labels = list(edu_dist.keys())
        edu_probs = list(edu_dist.values())
        education = rng.choice(edu_labels, p=edu_probs)
        income_options = INCOME_BY_CITY.get(tier, INCOME_BY_CITY["二线"])
        if education == "硕士+":
            income_idx = min(len(income_options) - 1, rng.integers(2, len(income_options)))
        elif education == "本科":
            income_idx = min(len(income_options) - 1, rng.integers(1, len(income_options)))
        else:
            income_idx = rng.integers(0, len(income_options))
        income = income_options[income_idx]
        n_interests = rng.integers(2, 6)
        interests = rng.choice(INTERESTS, size=n_interests, replace=False).tolist()
        big_five = {label: round(float(rng.uniform(0.2, 0.95)), 2) for label in BIG_FIVE_LABELS}
        wechat_habit = rng.choice(WECHAT_HABITS)
        reading_style = rng.choice(["碎片化扫标题", "认真读完再判断", "看作者名决定", "看封面图决定"])
        personas.append({
            "id": i + 1,
            "age": int(age),
            "age_label": age_label,
            "gender": gender,
            "city": city,
            "city_tier": tier,
            "occupation": occupation,
            "education": education,
            "income": income,
            "interests": interests,
            "big_five": big_five,
            "wechat_habit": wechat_habit,
            "reading_style": reading_style,
        })
    return personas


def build_prompt(persona: dict, title: str) -> str:
    interests_str = "、".join(persona["interests"])
    personality_parts = []
    bf = persona["big_five"]
    if bf["开放性"] > 0.7:
        personality_parts.append("喜欢尝试新东西")
    if bf["开放性"] < 0.3:
        personality_parts.append("比较保守，不喜欢风险")
    if bf["外向性"] > 0.7:
        personality_parts.append("爱社交爱分享")
    if bf["外向性"] < 0.3:
        personality_parts.append("比较内向低调")
    if bf["情绪稳定性"] < 0.4:
        personality_parts.append("容易焦虑")
    personality_str = "，".join(personality_parts) if personality_parts else "性格中性"

    return f"""你是{persona['age']}岁{persona['gender']}性，住在{persona['city']}（{persona['city_tier']}城市），{persona['occupation']}，学历{persona['education']}，月收入{persona['income']}。
你平时关注：{interests_str}。
性格特点：{personality_str}。
公众号使用习惯：{persona['wechat_habit']}，阅读时倾向于{persona['reading_style']}。

现在你在微信公众号列表里刷到了这个标题：
「{title}」

请判断你会不会点开看。

严格按以下 JSON 格式回复（不要加任何其他文字）：
{{"click": true或false, "reason": "一句话说明原因"}}"""


def call_llm(api_base: str, api_key: str, model: str, prompt: str, timeout: int = 30) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    try:
        r = httpx.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=timeout)
        r.raise_for_status()
        resp = r.json()
        text = resp["choices"][0]["message"].get("content", "").strip()
        try:
            clean = text.strip("`").strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()
            result = json.loads(clean)
            return {
                "click": bool(result.get("click", False)),
                "reason": str(result.get("reason", "")),
                "raw": text,
            }
        except json.JSONDecodeError:
            clicked = "true" in text.lower()[:20] or text.startswith("点") or "会点" in text[:10]
            return {
                "click": clicked,
                "reason": text[:60],
                "raw": text,
                "parse_fallback": True,
            }
    except Exception as e:
        return {"click": None, "reason": f"error: {str(e)[:50]}", "raw": "", "error": True}


def vote_one(args_tuple):
    """单次投票，供 ThreadPoolExecutor 调用"""
    persona, title, api_base, api_key, model = args_tuple
    prompt = build_prompt(persona, title)
    result = call_llm(api_base, api_key, model, prompt)
    result["persona_id"] = persona["id"]
    result["persona_summary"] = f"{persona['age']}岁{persona['gender']}·{persona['city']}·{persona['occupation']}·{persona['income']}"
    return result


def main():
    parser = argparse.ArgumentParser(description="公众号标题 AI 测试工具")
    parser.add_argument("--titles", nargs="+", required=True, help="待测标题列表")
    parser.add_argument("--souls", type=int, default=100, help="AI persona 数量 (default: 100)")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API base URL")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="API key, or set TITLE_REVIEWER_API_KEY")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="模型名称")
    parser.add_argument("--concurrency", type=int, default=5, help="并发数 (default: 5)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--no-save", action="store_true", help="不保存结果文件")
    args = parser.parse_args()
    if not args.api_key:
        parser.error("API key required: pass --api-key or set TITLE_REVIEWER_API_KEY")

    print(f"🚀 模型: {args.model} | Souls: {args.souls} | 并发: {args.concurrency}")
    print(f"   API: {args.api_base}")

    # 生成 persona
    print(f"\n👥 生成 {args.souls} 个 AI persona（借鉴 Oransim 人口学分布）...")
    personas = generate_personas(args.souls, seed=args.seed)

    age_dist = Counter(p["age_label"] for p in personas)
    gender_dist = Counter(p["gender"] for p in personas)
    tier_dist = Counter(p["city_tier"] for p in personas)
    print(f"   年龄: {dict(age_dist)}")
    print(f"   性别: {dict(gender_dist)}")
    print(f"   城市: {dict(tier_dist)}")

    all_results = []
    total_start = time.time()

    for ti, title in enumerate(args.titles, 1):
        print(f"\n📊 [{ti}/{len(args.titles)}] {title[:40]}...")
        title_start = time.time()

        # 构建并发任务
        tasks = [
            (p, title, args.api_base, args.api_key, args.model)
            for p in personas
        ]

        votes = []
        completed = 0
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = {pool.submit(vote_one, t): t[0] for t in tasks}
            for future in as_completed(futures):
                result = future.result()
                votes.append(result)
                completed += 1

                # 进度显示
                if result.get("click") is True:
                    sys.stdout.write("✓")
                elif result.get("click") is False:
                    sys.stdout.write("✗")
                else:
                    sys.stdout.write("?")

                if completed % 20 == 0:
                    clicked_so_far = sum(1 for v in votes if v.get("click") is True)
                    valid_so_far = sum(1 for v in votes if v.get("click") is not None)
                    sys.stdout.write(f" ({clicked_so_far}/{valid_so_far})")
                sys.stdout.flush()

        # 统计
        clicked = sum(1 for v in votes if v.get("click") is True)
        not_clicked = sum(1 for v in votes if v.get("click") is False)
        errors = sum(1 for v in votes if v.get("click") is None)
        valid = clicked + not_clicked
        ctr = round(clicked / valid * 100, 1) if valid > 0 else 0
        elapsed = round(time.time() - title_start, 1)

        reasons_click = [v["reason"] for v in votes if v.get("click") is True and v.get("reason") and not v.get("error")]
        reasons_skip = [v["reason"] for v in votes if v.get("click") is False and v.get("reason") and not v.get("error")]

        title_result = {
            "title": title,
            "clicked": clicked,
            "not_clicked": not_clicked,
            "errors": errors,
            "valid": valid,
            "ctr": ctr,
            "elapsed_s": elapsed,
            "reasons_click": reasons_click[:10],
            "reasons_skip": reasons_skip[:10],
            "votes": votes,
        }
        all_results.append(title_result)
        print(f"\n   ✅ CTR: {ctr}% ({clicked}/{valid}) | {elapsed}s | err:{errors}")

    # 排名
    all_results.sort(key=lambda x: x["ctr"], reverse=True)
    total_elapsed = round(time.time() - total_start, 1)

    print("\n" + "=" * 70)
    print("🏆 公众号标题 CTR 排名")
    print("=" * 70)
    for rank, r in enumerate(all_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"  {emoji} #{rank} CTR={r['ctr']}% ({r['clicked']}/{r['valid']}) | {r['title'][:45]}")

    print("\n💬 点击理由（Top 3）:")
    for r in all_results[:3]:
        print(f"  📈 {r['title'][:35]} (CTR {r['ctr']}%)")
        for reason in r["reasons_click"][:5]:
            print(f"      ✓ {reason}")
        if r["reasons_skip"]:
            print(f"    跳过理由:")
            for reason in r["reasons_skip"][:3]:
                print(f"      ✗ {reason}")

    # 保存
    if not args.no_save:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        model_slug = args.model.replace("/", "-")
        outfile = RESULTS_DIR / f"wechat-title-{model_slug}-s{args.souls}-{timestamp}.json"
        output = {
            "timestamp": timestamp,
            "tool": "wechat-title-tester v3.0",
            "config": {
                "model": args.model,
                "api_base": args.api_base,
                "n_souls": args.souls,
                "concurrency": args.concurrency,
                "seed": args.seed,
            },
            "persona_summary": {
                "age_dist": dict(age_dist),
                "gender_dist": dict(gender_dist),
                "city_tier_dist": dict(tier_dist),
            },
            "ranking": all_results,
            "total_elapsed_s": total_elapsed,
        }
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {outfile}")

    print(f"\n⏱️ 总耗时: {total_elapsed}s | 平均每标题: {total_elapsed/len(args.titles):.1f}s")
    return all_results


if __name__ == "__main__":
    main()
