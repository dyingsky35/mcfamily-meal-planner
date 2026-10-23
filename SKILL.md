---
name: 麦麦家庭餐规划助手
description: 基于麦当劳 MCP 的家庭一日三餐规划 Skill。输入家庭人数、单日预算、营养目标与忌口，调用麦当劳菜单/营养/价格/优惠券只读能力，生成可执行的家庭餐方案与可视化报告。仅做规划与查询，不调用任何写操作（如下单/领券）。适用于精打细算的家庭用户、关注营养搭配的父母、麦当劳高频消费者，以及想用最低成本体验麦当劳 MCP 的开发者。
---

# 麦麦家庭餐规划助手（McFamily Meal Planner）

## 定位
把"今天全家吃什么、花多少钱、营养够不够"这三件事，用麦当劳真实数据一次性算清楚。
不是又一个"点餐助手"，而是面向**家庭单位**的**一日营养+预算联合规划**——当前参赛作品里较少覆盖的空白场景。

## 触发场景
- "帮我家三口人规划今天的麦当劳，预算 120，要均衡，不吃辣"
- "两个人减脂期，麦当劳怎么吃不超过 80 块还能吃饱"
- "用麦当劳 MCP 给我出一份家庭套餐方案，带营养报告"

## 执行流程
1. 通过 `mcd-mcp` 拉取真实菜单与营养/价格数据（见下方工具依赖）；若用户尚未配置 Token，则回退到仓库内置 `src/sample_menu.json` 演示数据，并提示用户配置后可获得实时结果。
2. 营养数据经 `src/toon_parser.py` 解析（`list-nutrition-foods` 返回 TOON 文本，非 JSON）。
3. 调用本仓库 `src/planner.py` 生成方案：
   - `--people` 家庭人数
   - `--budget` 家庭单日总预算（元）
   - `--goal` 营养目标：`均衡` / `减脂` / `增肌`
   - `--avoid` 忌口标签（逗号分隔，如 `辣,牛肉`）
4. 输出 HTML 报告（样式同 `examples/demo_report.html`），含分餐明细、营养达成度进度条、预算结余与优惠券提示。

## 工具依赖（mcd-mcp，仅只读）
- 时段：`now-time-info`
- 营养：`list-nutrition-foods`（TOON，由 `src/toon_parser.py` 解析）
- 门店与菜单：`query-nearby-stores` / `query-meals` / `query-meal-detail`
- 优惠券（仅查询提示）：`query-store-coupons` / `query-my-coupons`
- 算价：`calculate-price`（返回单位为分，展示÷100）
- **不调用** `create-order` / `cancel-order` / `auto-bind-coupons` / `draw-lottery` 等写操作。

## 配置（WorkBuddy 自定义连接器）
脱敏模板见本仓库 `mcp-config.example.json`：
```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
    }
  }
}
```
真实 Token 通过环境变量 `MCD_MCP_TOKEN` 注入，**绝不写死进仓库**（避免会员账号钥匙泄露）。

## 备注
- 规划引擎与解析器均为纯标准库 Python，零外部依赖，开箱即跑。
- 输出仅供参考，不构成营养或专业建议（见 CONTEST_DECLARATION.md 使用提示）。
- 本 Skill 只做规划与查询，不下单、不领券；如需下单请在麦当劳官方渠道完成（钱由人付）。
