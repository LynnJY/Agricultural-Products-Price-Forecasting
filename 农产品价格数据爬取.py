#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2025/4/10
# @Author : Lynn
# @Describe : 多线程农产品批发价格批量爬取并保存为CSV

import requests
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# 关闭 SSL 验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 请求头
headers = {
    "Host": "ncpscxx.moa.gov.cn",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://ncpscxx.moa.gov.cn",
    "Referer": "https://ncpscxx.moa.gov.cn/product-web/",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "close",
}

# 请求地址
url = "https://ncpscxx.moa.gov.cn/product/homeWholesalePrice/selectWholesalePrice"

# 产品ID列表（可自行扩展）
product_id_list = [
    "AL01002001", "AL01006","AL01010","AL02001016","AL05001","AE01001","AE01002001","AE01003","AE01005","AE01006","AE01019", "AE02001002", "AE02002", "AE02003", "AE02006", "AE02007", "AE02008", "AE02009",
    "AE02011", "AE02012", "AE02014", "AE03008", "AE04001", "AE04003", "AE04004", "AE04005",
    "AE04006", "AE04008", "AE04009", "AE04016", "AE05001001", "AE05001008", "AF01001001",
    "AF01002001", "AF02001001", "AF06001", "AF06002", "AF07001", "AM01001001", "AM01001002",
    "AM01002", "AM01003",
    "AM01004",
    # "AM02001001",
    # "AM02002"  宁夏没有这两个
]

# 固定参数
base_params = {
    "startTime": "20100110",
    "endTime": "20250410",
    "productClass1Code": "AL",
    "productClass2Code": "AL01",
    "marketName": "",
    "province": "宁夏",
    "timetype": "r",
}

# 请求并保存数据函数
def fetch_and_save(product_id):
    print(f"[线程] 正在爬取产品ID: {product_id}")
    params = base_params.copy()
    params["productId"] = product_id

    try:
        response = requests.post(url, headers=headers, params=params, verify=False, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                codes = data["data"]["codes"]
                dates = data["data"]["names"]
                values = data["data"]["values"]

                # 提取产品名并清洗为合法文件名
                product_name = codes[0] if codes else "未知产品"
                safe_product_name = re.sub(r'[\\/:*?"<>|]', "_", product_name)

                # 准备CSV数据
                csv_data = []
                for i, product in enumerate(codes):
                    for j, date in enumerate(dates):
                        price = values[i][j] if j < len(values[i]) else None
                        csv_data.append({
                            "日期": date,
                            "产品": product,
                            "价格": price,
                        })

                # 保存CSV文件
                csv_file = f"农产品批发价格数据_{safe_product_name}.csv"
                with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=["日期", "产品", "价格"])
                    writer.writeheader()
                    writer.writerows(csv_data)

                print(f"[完成] 数据已保存到 {csv_file}")
            else:
                print(f"[失败] 请求失败: {data.get('msg', '未知错误')}")
        else:
            print(f"[失败] HTTP 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[错误] 请求异常: {e}")

# 设置线程池
MAX_WORKERS = 3  # 同时运行的线程数，可根据网速调节

def main():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {executor.submit(fetch_and_save, pid): pid for pid in product_id_list}
        for future in as_completed(future_to_id):
            product_id = future_to_id[future]
            try:
                future.result()
            except Exception as exc:
                print(f"[异常] 产品ID: {product_id} 发生异常: {exc}")

if __name__ == "__main__":
    main()