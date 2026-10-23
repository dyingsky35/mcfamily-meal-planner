#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦家庭餐规划助手 — 规划引擎 (planner.py)
依赖：仅 Python 标准库（json / argparse / datetime / pathlib / html），零外部依赖。

数据源（双路径）：
  1) 真实路径：由 WorkBuddy 通过 mcd-mcp 工具拉取菜单/营养/价格/优惠券后传入（见 SKILL.md）。
  2) 演示路径：内置 sample_menu.json，无需 Token 即可本地运行，用于验证与提交示例。
"""
import json
import argparse
import datetime
from pathlib import Path

# 每日每成人营养目标（近似参考值，非专业营养建议）
GOAL_TARGETS = {
    "均衡": {"kcal": 2000, "protein": 60, "fat": 70, "carb": 250},
    "减脂": {"kcal": 1500, "protein": 75, "fat": 45, "carb": 150},
    "增肌": {"kcal": 2600, "protein": 110, "fat": 80, "carb": 320},
}
MEAL_ORDER = ["早餐", "午餐", "晚餐"]
MEAL_BUDGET_RATIO = {"早餐": 0.25, "午餐": 0.40, "晚餐": 0.35}


def load_menu(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def plan(menu, people, budget, goal, avoid):
    """为家庭规划一日三餐。返回 (分餐结果, 营养目标, 实际花费)。"""
    if goal not in GOAL_TARGETS:
        raise ValueError(f"goal 必须是 {list(GOAL_TARGETS)} 之一")
    target = {k: v * people for k, v in GOAL_TARGETS[goal].items()}
    result = {m: [] for m in MEAL_ORDER}
    remaining = dict(target)
    spent = 0.0
    for meal in MEAL_ORDER:
        meal_budget = budget * MEAL_BUDGET_RATIO[meal]
        cands = [
            m for m in menu
            if (meal in m["meals"] or "任意" in m["meals"])
            and m["price"] <= meal_budget
            and not (set(m.get("tags", [])) & set(avoid))
        ]
        # 价值排序：蛋白质与热量密度 / 价格，优先填补缺口
        def value(m):
            return (m["protein"] * 2 + m["kcal"]) / max(m["price"], 1)
        cands.sort(key=value, reverse=True)
        meal_cost = 0.0
        picks = []
        for m in cands:
            if meal_cost + m["price"] <= meal_budget and len(picks) < 3:
                picks.append(m)
                meal_cost += m["price"]
                for k in ("kcal", "protein", "fat", "carb"):
                    remaining[k] = max(0, remaining[k] - m[k])
        result[meal] = picks
        spent += meal_cost
    return result, target, spent


def _bar(actual, target):
    pct = min(100, int(actual / target * 100)) if target else 0
    color = "#2e7d32" if pct >= 80 else ("#f9a825" if pct >= 50 else "#c62828")
    return (f'<div class="bar"><div class="fill" style="width:{pct}%;'
            f'background:{color}"></div></div><span>{pct}%</span>')


def render_html(result, target, spent, people, budget, goal, avoid):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    total = {k: 0 for k in ("kcal", "protein", "fat", "carb")}
    rows = []
    for meal in MEAL_ORDER:
        items = result[meal]
        meal_html = ""
        for it in items:
            for k in total:
                total[k] += it[k]
            meal_html += (
                f'<tr><td>{it["name"]}</td>'
                f'<td>{it["kcal"]}</td><td>{it["protein"]}</td>'
                f'<td>{it["fat"]}</td><td>{it["carb"]}</td>'
                f'<td>¥{it["price"]:.1f}</td></tr>'
            )
        if not items:
            meal_html = '<tr><td colspan="6" class="empty">（本餐未选入，可手动补充）</td></tr>'
        rows.append(
            f'<h3>{meal}</h3>'
            f'<table class="items"><tr><th>餐品</th><th>热量</th><th>蛋白</th>'
            f'<th>脂肪</th><th>碳水</th><th>价格</th></tr>{meal_html}</table>'
        )
    bars = "".join(
        f'<div class="metric"><label>{label}</label>{_bar(total[k], target[k])}'
        f'<small>{total[k]}/{target[k]} {unit}</small></div>'
        for label, k, unit in [
            ("热量", "kcal", "kcal"), ("蛋白质", "protein", "g"),
            ("脂肪", "fat", "g"), ("碳水", "carb", "g"),
        ]
    )
    avoid_txt = "、".join(avoid) if avoid else "无"
    if spent >= budget * 0.95:
        tip = "已接近预算上限，可微调餐品组合压缩成本。"
    else:
        tip = (f"还可结余约 ¥{budget - spent:.1f}，"
               "建议叠加麦当劳优惠券进一步节省。")
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>麦麦家庭餐规划报告</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#222}}
h1{{font-size:22px}} h3{{margin:18px 0 6px;color:#d52b1e}}
.meta{{color:#666;font-size:13px}}
table.items{{width:100%;border-collapse:collapse;font-size:14px}}
table.items th,table.items td{{border:1px solid #eee;padding:6px 8px;text-align:center}}
table.items th{{background:#fafafa}}
.empty{{color:#999}}
.metrics{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}}
.metric{{flex:1;min-width:160px}}
.metric label{{display:block;font-size:13px;color:#555}}
.bar{{background:#eee;border-radius:6px;height:10px;overflow:hidden;margin:4px 0}}
.fill{{height:100%}}
.metric small{{color:#888;font-size:12px}}
.tip{{background:#fff8e1;border-left:4px solid #f9a825;padding:10px 12px;font-size:14px;margin-top:16px}}
</style></head><body>
<h1>🍔 麦麦家庭餐规划报告</h1>
<div class="meta">生成时间：{now} ｜ 目标：{goal} ｜ 人数：{people} ｜ 预算：¥{budget:.0f} ｜ 忌口：{avoid_txt}</div>
<div class="metrics">{bars}</div>
{''.join(rows)}
<div class="tip">💡 {tip}。本报告由「麦麦家庭餐规划助手」基于麦当劳公开菜单数据生成，仅供参考，不构成营养或专业建议。</div>
</body></html>"""


def main():
    ap = argparse.ArgumentParser(description="麦麦家庭餐规划助手")
    ap.add_argument("--people", type=int, default=3, help="家庭人数")
    ap.add_argument("--budget", type=float, default=120.0, help="家庭单日总预算(元)")
    ap.add_argument("--goal", default="均衡", choices=list(GOAL_TARGETS), help="营养目标")
    ap.add_argument("--avoid", default="", help="忌口标签，逗号分隔，如 辣,牛肉")
    ap.add_argument("--menu", default=str(Path(__file__).with_name("sample_menu.json")))
    ap.add_argument("--out", default="examples/demo_report.html")
    args = ap.parse_args()
    avoid = [a.strip() for a in args.avoid.split(",") if a.strip()]
    menu = load_menu(args.menu)
    result, target, spent = plan(menu, args.people, args.budget, args.goal, avoid)
    html_out = render_html(result, target, spent, args.people, args.budget, args.goal, avoid)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"已生成报告：{out_path}")
    print(f"目标：{args.goal} 人数：{args.people} 预算：¥{args.budget:.0f} 实际花费：¥{spent:.1f} 忌口：{avoid or '无'}")


if __name__ == "__main__":
    main()
