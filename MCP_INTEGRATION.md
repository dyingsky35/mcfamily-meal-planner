# MCP 接入说明（MCP_INTEGRATION.md）

## 1. 使用的麦当劳 MCP Server

| 项 | 值 |
|---|---|
| Server 名称 | `mcd-mcp` |
| 接入方式 | Streamable HTTP（远程 MCP，端点为根路径 `/`，非 `/mcp`） |
| 地址 | `https://mcp.mcd.cn` |
| 鉴权 | `Authorization: Bearer <MCP_TOKEN>`（Token 由 open.mcd.cn 控制台免费申请，**代表你的麦当劳会员身份，严禁分享/提交到仓库或截图**） |
| 限流 | 每个 Token 600 次/分钟；`401`=Token 失效，`429`=触发限流 |
| 脱敏配置模板 | 本仓库 `mcp-config.example.json`（仅环境变量占位符，赛事强制提交） |

> 工具（Tool）完整列表与契约以官方 [mcd-mcp-server](https://github.com/M-China/mcd-mcp-server) 仓库为准。本 Skill 仅依赖其中的**只读**能力（菜单 / 营养 / 价格 / 优惠券），**不调用任何写操作**。

## 2. 实际调用的 Tool 与用途

| 能力 | 对应 mcd-mcp 工具 | 在 Skill 中的用途 |
|---|---|---|
| 当前时段 | `now-time-info` | 早/午/晚/夜市分流，决定可点菜单 |
| 餐品营养 | `list-nutrition-foods` | 获取热量/蛋白/脂肪/碳水/钠/钙，作为营养基线（返回 **TOON 文本**，由 `src/toon_parser.py` 解析） |
| 附近门店 | `query-nearby-stores` | 取 `storeCode`，决定菜单与价格 |
| 门店菜单 | `query-meals` | 获取餐品、编码与单价（**价格单位为「元」，且多为字符串**） |
| 套餐明细 | `query-meal-detail` | 拆解套餐 rounds 与可替换项（替换只能在同一 round 内） |
| 优惠券 | `query-store-coupons` / `query-my-coupons` | 在报告中提示可叠加优惠（**不做自动领券/下单**） |
| 算价 | `calculate-price` | 计算到手价（**返回单位为「分」，展示需 ÷100**） |

> **本 Skill 明确不调用** `create-order` / `cancel-order` / `auto-bind-coupons` / `draw-lottery` 等写操作。
> 我们只做「规划 + 查询」，把"是否真实下单"完全交还用户，符合赛事安全边界与麦当劳官方红线（钱由人付）。

## 3. 调用流程（业务价值）

```
用户需求（人数 / 预算 / 目标 / 忌口）
        │
        ▼
now-time-info → query-nearby-stores → query-meals → query-meal-detail
        │
        ▼
list-nutrition-foods → src/toon_parser.py（解析 TOON）→ 本地营养索引
        │
        ▼
planner.py：在预算内、按营养目标（均衡/减脂/增肌）、过滤忌口，本地枚举组合
（先本地求解，再对少量候选调 calculate-price，避免触发 600/min 限流）
        │
        ▼
render_html：分餐明细 + 营养达成度 + 预算结余 + 优惠券提示（仅提示，不下单）
```

**业务价值**：把分散的菜单、营养、价格、优惠信息，用 MCP 一次性聚合成家庭可决策的方案，降低"点什么、花多少、够不够营养"的决策成本；相比单纯"点餐/省钱"助手，本 Skill 切入的是**家庭单位的一日营养—预算联合规划**这一更贴近真实生活的空白场景。

## 4. 已踩实的接口契约（实测要点）

1. `list-nutrition-foods` 返回 **TOON 文本而非 JSON**；`nutritionDescription` 可能为空也可能含逗号 → 由 `src/toon_parser.py` 按"首段=名称、末 7 段=数值、中间=描述"稳健解析。
2. `query-meals` 价格单位为**「元」且多为字符串**；`calculate-price` 返回**「分」** → 展示层必须统一换算，否则价格会差 100 倍。
3. 套餐替换只能发生在**同一 round 的候选项**内（如"薯条换玉米杯"未必可行，需以 `query-meal-detail` 为准）。
4. `create-order` 属于真实写操作，**本 Skill 不调用**；任何下单需求交由用户在官方渠道完成。

## 5. 容错设计

- 未配置 MCP Token 时，自动回退到仓库内置 `src/sample_menu.json`，保证 Skill 在无凭证环境下仍可演示与提交（评委 clone 后可直接 `python src/planner.py` 验证）。
- 真实路径下，营养数据经 `toon_parser.py` 解析后与 `query-meals` 的价格/餐段/标签合并，再喂给 `planner.py`。
- 所有营养目标均为近似参考值，输出明确标注"仅供参考，不构成专业建议"。
