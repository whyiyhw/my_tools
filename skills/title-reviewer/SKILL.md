---
name: title-reviewer
description: 用 AI 模拟用户对公众号/小红书标题进行点击率预测测试。生成多样化 persona，投票点/不点，输出 CTR 排名和理由。触发词：测标题、标题测试、标题评审、title test、选标题、title review。
---

# Title Reviewer — AI 模拟用户测标题点击率

用 AI persona 对多个标题投票，预测哪个点击率最高。

## 默认：mimo-v2.5-pro × 5并发

默认全走 **mimo-v2.5-pro**，5 并发。API key 通过 `TITLE_REVIEWER_API_KEY` 环境变量或 `--api-key` 参数传入。

```bash
# 基本用法
python3 scripts/wechat-title-tester.py \
  --api-key YOUR_KEY \
  --titles "标题1" "标题2" "标题3" \
  --souls 50

# 指定其他模型
python3 scripts/wechat-title-tester.py \
  --api-base https://open.bigmodel.cn/api/paas/v4 \
  --api-key YOUR_KEY \
  --model glm-4.5-flash \
  --titles "标题1" "标题2"
```

## 参数说明

| 参数 | 说明 | 默认 |
|------|------|------|
| `--titles` | 待测标题列表（必填） | - |
| `--souls` | AI persona 总数 | 100 |
| `--concurrency` | 并发请求数 | **5** |
| `--api-base` | API URL | mimo |
| `--api-key` | API key，也可用 `TITLE_REVIEWER_API_KEY` | 环境变量 |
| `--model` | 模型名 | mimo-v2.5-pro |
| `--seed` | 随机种子 | 42 |
| `--no-save` | 不保存结果 | false |

## 硬编码默认配置

| 项目 | 值 |
|------|-----|
| 模型 | **mimo-v2.5-pro** |
| API Base | `https://token-plan-sgp.xiaomimimo.com/v1` |
| max_tokens | 2048 |
| 并发 | 5 |

API key 不写入仓库；使用前设置 `TITLE_REVIEWER_API_KEY`，或调用时传 `--api-key`。

## 输出

- 控制台：CTR 排名 + 点击/跳过理由
- 文件：`oransim-title-tests/wechat-title-mimo-v2.5-pro-s{souls}-{timestamp}.json`
- JSON 含：每个 persona 的投票详情、完整理由、人口学分布统计

## 速度参考（5并发 + mimo-v2.5-pro）

| Souls | 标题数 | 预计耗时 |
|-------|--------|----------|
| 20 | 5 | ~8 min |
| 50 | 5 | ~18 min |
| 100 | 5 | ~35 min |

## Persona 分布（借鉴 Oransim 人口学）

- **年龄**：18-65 岁，6 个年龄段
- **性别**：男 48% / 女 52%
- **城市**：一线 ~ 新一线 ~ 二线 ~ 三线 ~ 四五线
- **职业**：按年龄段分布
- **教育**：按年龄段分布
- **收入**：按城市分级 + 教育加权
- **兴趣**：20 个公众号相关标签，随机 2-5 个
- **性格**：Big Five 简化版
- **公众号使用习惯**：5 种阅读模式

## 相关文件

- 脚本：`scripts/wechat-title-tester.py`
- Oransim 官方版：`scripts/oransim-title-test.py`（小红书场景）
- 结果目录：`oransim-title-tests/`
