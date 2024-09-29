# coding=utf-8
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import pandas as pd
import folium
from folium.plugins import HeatMap

import cpca
from cpca import _init_data
ad_2_addr_dict, matcher = _init_data()  # 初始化 adcode 数据和 matcher

from util.log_utils import logger

def get_lat_lon(city: str) -> tuple:
    """
    使用 cpca 获取城市的经纬度信息，如果无法匹配则返回 (None, None)
    """
    # 使用 cpca 提取省市区信息
    location_df = cpca.transform([city], pos_sensitive=True)
    # 检查 DataFrame 是否为空
    if location_df.empty:
        logger.log_info(f"城市 {city} 无法解析，跳过。")
        return None, None
    # 尝试获取 adcode
    adcode = location_df.iloc[0].get('adcode')
    if pd.isna(adcode):
        logger.log_info(f"城市 {city} 无法获取 adcode，跳过。")
        return None, None
    # 从 adcode 获取地址信息
    addr_info = ad_2_addr_dict.get(adcode.ljust(12, '0'))
    if addr_info:
        return float(addr_info.latitude), float(addr_info.longitude)
    else:
        logger.log_info(f"城市 {city} 的 adcode 未找到匹配的地址信息，跳过。")
        return None, None

def create_heatmap(city_count: pd.DataFrame, kind = 'province', heatmap_html_path = None) -> str:
    data = []
    # 设置默认HTML路径
    heatmap_html_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        f'figures/{kind}_heatmap.html'
    ) if heatmap_html_path is None else heatmap_html_path
    
    # 遍历每个城市及其计数
    for idx, row in city_count.iterrows():
        city = row[0]
        count = row[1] * 100
        # 获取城市的经纬度信息
        try:
            lat, lon = get_lat_lon(city)
        except Exception as e:
            lat, lon = None, None
            logger.log_exception()
        if lat is None or lon is None:
            logger.log_info(f"{kind} : {city} 无法找到经纬度，跳过。")
            continue
        # 将城市的经纬度及计数信息加入列表
        data.append([lat, lon, count])
    # 创建 Folium 地图对象
    m = folium.Map(location=[35.8617, 104.1954], zoom_start=5)  # 以中国为中心
    # 将热力图数据添加到地图上
    HeatMap(data).add_to(m)
    # 保存生成的地图为 HTML 文件
    m.save(heatmap_html_path)
    
    return heatmap_html_path