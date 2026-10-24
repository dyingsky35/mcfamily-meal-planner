# 🍔 麦麦家庭餐规划助手（McFamily Meal Planner）

基于 **麦当劳 MCP** 的家庭一日三餐规划 Skill —— 输入家庭人数、单日预算、营养目标与忌口，调用麦当劳真实菜单 / 营养 / 价格 / 优惠券只读能力，生成可执行的家庭餐方案与可视化报告。

> 参赛作品：WorkBuddy × 麦当劳「1024 程序员节·程序员创意开发大赛」
> 仓库要求公开、含规定文件（本仓库已齐备：README / CONTEST_DECLARATION.md / MCP_INTEGRATION.md / 源代码 / workbuddy.md / mcp-config.example.json）。

---

## ✨ 功能亮点

- **家庭单位规划**：以"全家一天"为粒度，而非单人单餐，更贴近真实决策。
- **营养 × 预算联合优化**：按目标（均衡 / 减脂 / 增肌）设定营养基线，在预算内自动选品。
- **忌口过滤**：辣 / 牛肉 / 猪肉 / 鸡肉 / 海鲜 / 甜 等标签可组合排除。
- **可视化报告**：HTML 报告含分餐明细、营养达成度进度条、预算结余与优惠券提示。
- **双数据源**：配置了麦当劳 MCP Token 走真实数据；未配置时回退内置样例数据，开箱即跑。
- **只读安全**：仅调用菜单/营养/价格/优惠券查询能力，**不调用 create-order 等写操作**，钱由人付。

## 🚀 快速开始（本地演示，无需 Token）

```bash
# 需要 Python 3.8+（仅用标准库，无需 pip install）
python src/planner.py --people 3 --budget 120 --goal 均衡 --avoid 辣,牛肉
# 生成的报告在 examples/demo_report.html，浏览器打开即可
```

更多示例：

```bash
python src/planner.py --people 2 --budget 80  --goal 减脂
python src/planner.py --people 4 --budget 160 --goal 增肌 --avoid 牛肉
```

验证 TOON 解析器（演示 `list-nutrition-foods` 的真实返回格式处理）：

```bash
python src/toon_parser.py src/sample_nutrition.toon
```

## 🔌 接入麦当劳 MCP（获得实时数据）

1. 打开 [open.mcd.cn](https://open.mcd.cn)，手机号登录 → 控制台 → 激活并复制 **MCP Token**（Token 代表你的麦当劳会员身份，严禁分享）。
2. 在 WorkBuddy 的**连接器**中添加 `mcd-mcp`（Streamable HTTP，地址 `https://mcp.mcd.cn`），鉴权头填 `Authorization: Bearer <你的Token>`。
3. 启用 `mcd-mcp`，在对话框直接使用本 Skill（详见 `SKILL.md`）。

> 仓库内的 `mcp-config.example.json` 为**脱敏模板**（仅 `${MCD_MCP_TOKEN}` 环境变量占位符），请据此配置，真实 Token 通过环境变量注入，**勿提交进仓库或出现在截图**。

## 🌐 在线体验（无需安装，30 秒上手）

不想装 Python？直接打开在线版，输入家庭人数 / 单日预算 / 营养目标 / 忌口，实时生成可执行的家庭餐方案与预算结余：

👉 **https://xiaoxin-workbench-54232.app.workbuddy.host/**

在线版与仓库内 `webapp/index.html` 同源，均为**单文件静态页**，可下载到本地双击打开，逻辑与 `src/planner.py` 完全一致（内置 22 款麦当劳样例餐品，开箱即跑）。

## 📁 目录结构

```
.
├── README.md                  # 本文件（项目介绍/安装/使用）
├── CONTEST_DECLARATION.md     # 参赛声明（官方文件，内容不可改）
├── MCP_INTEGRATION.md         # 麦当劳 MCP 接入说明（含真实接口契约踩坑）
├── SKILL.md                   # WorkBuddy Skill 定义
├── workbuddy.md               # WorkBuddy 开发上下文（专项奖核验用）
├── mcp-config.example.json    # 脱敏 MCP 配置示例（强制提交，仅环境变量占位符）
├── LICENSE
├── src/
│   ├── planner.py             # 规划引擎（纯标准库）
│   ├── toon_parser.py         # 麦当劳营养 TOON 文本解析器（纯标准库）
│   ├── sample_menu.json       # 演示用样例菜单（价格单位：元）
│   └── sample_nutrition.toon  # 演示用营养 TOON 样本（含含逗号描述）
├── webapp/
│   └── index.html             # 单文件交互体验页（无需后端，浏览器直接打开 / 在线版同源）
└── examples/
    ├── demo_report.html       # 示例报告（3人/120元/均衡/忌辣牛肉）
    └── demo_report_2.html     # 示例报告（2人/80元/减脂）
```

## 🎯 目标用户

- 精打细算、希望"吃得明白又省钱"的家庭用户
- 关注营养搭配、有减脂 / 增肌目标的父母
- 麦当劳高频消费者、学生党、上班族
- 想用最低成本体验麦当劳 MCP 能力的开发者

## 📌 参赛说明

- 本作品为麦当劳程序员节创意开发大赛参赛作品，非麦当劳官方产品。
- 餐品信息、价格及供应状态以麦当劳官方渠道实时结果为准；输出仅供参考，不构成营养或专业建议。
- 报名方式见 [M-China/mcd-developer-innovation-challenge](https://github.com/M-China/mcd-developer-innovation-challenge) 官方仓库。
