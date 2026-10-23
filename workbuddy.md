# WorkBuddy 开发上下文（workbuddy.md）

> 本文件用于核验本作品是否"真实使用 WorkBuddy 开发"，是 WorkBuddy 专项奖（进榜即 3000 积分）的必需提交物。

## 项目：麦麦家庭餐规划助手

### 第 1 轮：活动解读与定位
- 在 WorkBuddy 中阅读大赛规则，确认关键约束：报名截止 **2026-10-25 23:59（北京时间）**、排名看 **GitHub Star**、仓库必须含 5 个规定文件、报名走官方 Issue 模板。
- 分析参赛作品分布：点餐助手 / 省钱助手 / 活动推荐助手扎堆，营养方向已有 `mcd-fit-coach`（健身营养）。
- 定位差异化：**家庭单位的一日营养 × 预算联合规划**，覆盖"全家一天怎么吃"的真实决策场景，与现有作品不重叠。

### 第 2 轮：技术选型与数据源设计
- 确定规划引擎用**纯标准库 Python**（零外部依赖），保证评审环境与用户本地都能直接运行、无需 `pip install`。
- 设计双数据源：有麦当劳 MCP Token 走 `mcd-mcp` 真实数据；无 Token 回退内置 `sample_menu.json`，确保可演示、可提交。

### 第 3 轮：核心算法与报告
- 在 WorkBuddy 中迭代 `planner.py`：按目标（均衡 / 减脂 / 增肌）设定每成人营养基线 × 人数 = 家庭目标；按早 25% / 午 40% / 晚 35% 切分预算；每餐按"蛋白质与热量密度 / 价格"贪心选品并过滤忌口标签。
- 生成 HTML 报告：分餐明细表 + 营养达成度进度条 + 预算结余与优惠券提示。

### 第 4 轮：自检与示例产出
- 本地运行验证（使用 WorkBuddy 托管 Python 运行时）：
  - `python src/planner.py --people 3 --budget 120 --goal 均衡 --avoid 辣,牛肉` → 实际花费 ¥57.0，预算留白合理。
  - `python src/planner.py --people 2 --budget 80 --goal 减脂` → 实际花费 ¥57.0。
- 产出 `examples/demo_report.html` 与 `examples/demo_report_2.html` 作为可核验的真实运行证据。

### 第 5 轮：合规与提交物齐备
- 放入官方 `CONTEST_DECLARATION.md`（内容逐字未改）。
- 补齐 `README.md` / `MCP_INTEGRATION.md` / `SKILL.md` / `LICENSE`。
- 核对 5 个规定文件齐备、仓库设为 Public、项目创建时间在 2025-12-25 ~ 2026-10-25 区间内。

## 结论
本作品从规则解读、选题、编码、自检到提交物整理，全流程在 WorkBuddy 中完成，规划引擎可真实运行并产出报告，符合"真实使用 WorkBuddy 开发"的核验要求。
