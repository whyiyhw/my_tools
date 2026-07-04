# V2EX Monitor - V2EX 精选内容监控

V2EX 社区每日精选推送，自动获取热门主题并发送到指定渠道。

## 功能

- 获取 V2EX 最新主题
- 根据热度（回复数）筛选内容
- 格式化输出
- 定时推送（默认每天 9:00）
- 支持多种渠道发送（Telegram、Discord 等）

## 使用方法

### 基础用法

```
帮我查看 V2EX 最新精选内容
```

### 手动推送

```
推送 V2EX 今日精选到 Telegram
```

### 配置说明

在 `USER.md` 中添加配置：

```yaml
v2ex:
  count: 5  # 精选数量
  min_replies: 3  # 最小回复数
  push_time: "09:00"  # 推送时间
  channels:
    - telegram  # 推送渠道
```

## 技术实现

- 使用 V2EX API: `https://www.v2ex.com/api/topics/latest.json`
- 内容筛选：基于回复数和创建时间
- 消息格式：Markdown
- 定时任务：通过 OpenClaw cron 系统
