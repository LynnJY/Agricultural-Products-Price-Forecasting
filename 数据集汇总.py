#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/4/10
# @Author : Lynn
# @Describe : 合并产品CSV为宽表，按日期为行，产品为列

import os
import pandas as pd

# 设置输入文件前缀和输出路径
prefix = "农产品批发价格数据_"
suffix = ".csv"
output_file = "农产品批发价格宽表.csv"

# 获取当前目录下所有符合命名规则的CSV文件
csv_files = [f for f in os.listdir('.') if f.startswith(prefix) and f.endswith(suffix)]

if not csv_files:
    print("❌ 未找到任何需要合并的CSV文件，请确认路径和文件名。")
else:
    print(f"🔍 共找到 {len(csv_files)} 个产品文件，开始合并为宽表...")

    # 用列表收集所有数据
    all_data = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)

            # 显示正在处理的文件和产品名
            product_name = df["产品"].iloc[0]
            print(f"✅ 正在处理：{file} -> 产品：{product_name}")

            all_data.append(df)

        except Exception as e:
            print(f"⚠️ 文件读取失败: {file}, 错误: {e}")

    if all_data:
        # 合并所有数据
        full_df = pd.concat(all_data, ignore_index=True)

        # 解析中文日期格式 "2011年1月1日"
        full_df["日期"] = pd.to_datetime(full_df["日期"], format='%Y年%m月%d日', errors='coerce')

        # 丢弃无法解析的日期
        full_df = full_df.dropna(subset=["日期"])

        # 透视表：行是日期，列是产品，值是价格
        pivot_df = full_df.pivot_table(index="日期", columns="产品", values="价格", aggfunc="first")

        # 重置索引并格式化日期
        pivot_df = pivot_df.reset_index()
        pivot_df["日期"] = pivot_df["日期"].dt.strftime('%Y-%m-%d')

        # 保存为CSV
        pivot_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n🎉 合并完成，宽表已保存为：{output_file}")
    else:
        print("❌ 没有成功读取任何数据，无法生成宽表。")