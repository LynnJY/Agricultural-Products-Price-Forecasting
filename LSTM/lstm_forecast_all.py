#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Lynn
# @Describe: 使用LSTM模型预测农产品未来30天价格（一个CSV对应一个产品）

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ---------- 参数设置 ----------
data_dir = "data"
file_prefix = "农产品批发价格数据_"
file_suffix = ".csv"
look_back = 7
predict_days = 30
epochs = 100
batch_size = 16
plot_dir = "plots"
output_dir = "forecast_result"

# ---------- 创建输出文件夹 ----------
os.makedirs(plot_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# ---------- 创建序列窗口 ----------
def create_dataset(data, look_back=7):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:i+look_back])
        y.append(data[i+look_back])
    return np.array(X), np.array(y)

# ---------- LSTM 预测函数 ----------
# ---------- LSTM 预测函数 ----------
def predict_with_lstm(product_name, df):
    print(f"\n🚀 开始处理产品：{product_name}")

    # 日期和价格预处理
    df["日期"] = pd.to_datetime(df["日期"], format="%Y年%m月%d日", errors='coerce')
    df = df.dropna(subset=["日期", "价格"])

    # 确保价格是数值型
    df["价格"] = pd.to_numeric(df["价格"], errors='coerce')
    df = df.dropna(subset=["价格"])

    # 按日期排序
    series = df.sort_values("日期")["价格"].values.reshape(-1, 1)

    # 标准化
    scaler = MinMaxScaler()
    series_scaled = scaler.fit_transform(series)

    # 创建训练数据
    X, y = create_dataset(series_scaled, look_back)
    if len(X) < 10:
        print(f"⚠️ 数据太少，跳过：{product_name}")
        return

    X = X.reshape((X.shape[0], look_back, 1))

    # 构建LSTM模型
    model = Sequential()
    model.add(LSTM(64, input_shape=(look_back, 1)))
    model.add(Dense(3))
    model.compile(optimizer='adam', loss='mse')

    # 训练模型
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    # 用最后一组数据预测未来30天
    forecast = []
    last_sequence = series_scaled[-look_back:].reshape(1, look_back, 1)
    for _ in range(predict_days):
        next_pred = model.predict(last_sequence)[0][0]
        forecast.append(next_pred)
        # 更新序列
        last_sequence = np.append(last_sequence[:, 1:, :], [[[next_pred]]], axis=1)

    # 反标准化预测结果
    forecast_inverse = scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()

    # 保存预测结果到CSV
    future_dates = pd.date_range(start=df["日期"].max() + pd.Timedelta(days=1), periods=predict_days)
    forecast_df = pd.DataFrame({
        "日期": future_dates.strftime("%Y年%m月%d日"),  # 日期格式改为中文格式
        "产品": product_name,                         # 加入产品列
        "价格": np.round(forecast_inverse, 2)         # 保留两位小数
    })
    forecast_df.to_csv(os.path.join(output_dir, f"LSTM预测_{product_name}.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ 预测完成：{product_name}，结果已保存。")

# ---------- 遍历所有CSV文件 ----------
files = [f for f in os.listdir(data_dir) if f.startswith(file_prefix) and f.endswith(file_suffix)]

if not files:
    print("❌ 没有找到CSV文件，请确认文件夹和命名。")
else:
    for file in files:
        try:
            df = pd.read_csv(os.path.join(data_dir, file))
            product_name = df["产品"].iloc[0]
            predict_with_lstm(product_name, df)
        except Exception as e:
            print(f"❌ 处理失败：{file}, 错误：{e}")