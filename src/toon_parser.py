#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦家庭餐规划助手 — 麦当劳 MCP 营养数据解析器 (toon_parser.py)

解决 list-nutrition-foods 返回 TOON 文本（非 JSON）的真实接口契约问题：
  - 首行为字段定义头：{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  - 数据行 nutritionDescription 可能为 null，也可能自带逗号 → 不能按固定位置 split

解析策略：
  - productName 取首段；
  - 尾部 7 个数值字段（energyKj, energyKcal, protein, fat, carbohydrate, sodium, calcium）取末尾 7 段；
  - 中间所有段合并为 nutritionDescription（处理含逗号的描述）。
输出与 planner.py 兼容的字典列表（name / kcal / protein / fat / carb / sodium / calcium）。

仅依赖 Python 标准库。
"""
import sys
import json
import argparse


def parse_toon(text: str):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return []
    header = lines[0].strip().strip("{}: ").strip()
    # 校验首行是否为字段定义头（含 productName 即可）
    if "productName" not in header:
        raise ValueError("TOON 首行不是字段定义头：%s" % header)
    out = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 9:
            continue
        name = parts[0].strip()
        tail = parts[-7:]
        desc_parts = parts[1:-7]
        desc = ",".join(desc_parts).strip() if desc_parts else ""
        try:
            nums = []
            for x in tail:
                x = x.strip()
                if x == "":
                    raise ValueError("空数值段")
                nums.append(float(x) if ("." in x or "e" in x.lower()) else int(x))
        except ValueError:
            continue
        rec = {
            "name": name,
            "nutritionDescription": None if desc.lower() == "null" or desc == "" else desc,
            "energyKj": nums[0],
            "kcal": nums[1],
            "protein": nums[2],
            "fat": nums[3],
            "carb": nums[4],
            "sodium": nums[5],
            "calcium": nums[6],
        }
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description="解析麦当劳 MCP TOON 营养数据")
    ap.add_argument("path", nargs="?", help="TOON 文本文件路径；省略则从 stdin 读取")
    args = ap.parse_args()
    if args.path:
        text = open(args.path, "r", encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    recs = parse_toon(text)
    print(json.dumps(recs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
