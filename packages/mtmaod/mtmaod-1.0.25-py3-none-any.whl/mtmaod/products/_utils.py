import numpy as np
import pandas as pd


def group_arr_by_nan(arr):
    """将数组按nan分组, 返回字典, key为非nan的索引, value为对应的行索引"""
    index_dict = {}
    for idx, t in enumerate(arr):
        a = ",".join(map(str, np.where(~np.isnan(t))[0]))
        if a in index_dict:
            index_dict[a].append(idx)
        else:
            index_dict[a] = [idx]
    return index_dict


def interp_aod_xxxtime(
    srcdata: pd.DataFrame,
    objtime: pd.DataFrame,
    method: str = "average",
    time_range: tuple = (-1800, 1800),
    ) -> pd.DataFrame:
    """插值AOD到指定时间

    Parameters
    ----------
    srcdata : pd.DataFrame
        原始的数据,一般为Aeronet站点数据, 默认值为 None
    objtime : pd.DataFrame
        目标时刻数据,一般为卫星产品的过境时刻,必须含有"timestamp"列,存储UTC时刻,或者数据的索引为UTC的pandas.datatime64类型
    method : str, optional
        插值的方法,有"average"和"linear"两种,average会取一段时间内数据平均,linear会进行相邻时刻数据的线性插值, 默认值为"average"
    time_range : tuple, optional
        时间范围,单位为秒,以目标时刻为基准(目标时刻为0)。默认值为(-1800, 1800),-1800表示目标时刻前1800秒,1800表示目标时刻后1800秒,将在这前后半小时内进行插值操作。

    Returns
    -------
    pd.DataFrame
        插值后的数据,包含有两列,第一列为插值后的AOD值,第二列为插值的计数,即插值用到的数据个数。数据的索引为数据的排序数目,即第几个数据。
    """
    # dataframe 必须 包含 timestamp 列
    # timestamps 必须 包含 timestamp 列
    srcdata = srcdata.copy()
    # 检查输入参数
    if isinstance(srcdata, pd.Series):
        srcdata = pd.DataFrame(srcdata)
    assert isinstance(srcdata, pd.DataFrame), "srcdata 必须是一个Pandas 中的 DataFrame 或其子类"
    assert isinstance(objtime, pd.DataFrame), "objtime 必须是一个Pandas 中的 DataFrame 或其子类"
    if (
        pd.api.types.is_datetime64_dtype(srcdata.index) or pd.api.types.is_datetime64tz_dtype(srcdata.index)
    ) and "timestamp" not in srcdata.columns:
        srcdata["timestamp"] = [i.timestamp() for i in srcdata.index]
    assert "timestamp" in srcdata.columns, "srcdata 必须 包含 timestamp 列"
    assert "timestamp" in objtime.columns, "objtime 必须 包含 timestamp 列"

    # # 第一步： 获取以目标时间为中心的时间段内的原始数据
    import geopandas as gpd
    from shapely.geometry import box

    # 构造时间box几何序列
    pre_time_offset, post_time_offset = time_range
    gs_obj = gpd.GeoSeries([box(i + pre_time_offset, -1, i + post_time_offset, 1) for i in objtime["timestamp"]])
    # 原始数据点转为point几何
    gs_src = gpd.GeoSeries(gpd.points_from_xy(srcdata["timestamp"], 0))
    # 获取查找表,此时的lookup_table是一个二维数组, 每一列表示一个目标和来源的匹配关系,第一行是目标的索引,第二行是来源的索引
    lookup_table = gs_src.sindex.query(gs_obj, predicate="intersects")

    # # 第二步： 根据匹配关系,插值目标时间点的AOD值
    df_src = srcdata.iloc[lookup_table[1]].copy()
    df_src["_idx"] = lookup_table[0]
    if method == "average":
        df_src.drop(columns=["timestamp"], inplace=True)
        result_temp = df_src.groupby("_idx").mean()
        counts = df_src.groupby("_idx").count()
        result_temp["counts"] = counts
        result_temp.index = np.array(objtime.index)[np.unique(lookup_table[0])]  # 将索引改为目标时间点的索引
    elif method == "linear":
        # 筛选能被插值的数据时间
        counts = df_src.groupby("_idx").count().iloc[:, 0]
        counts = counts[(counts > 1).values]
        objtime_interp = objtime.iloc[counts.index]
        # 插值
        result_temp = pd.DataFrame(index=objtime_interp.index)
        for column in df_src.columns:
            if column in ["timestamp", "_idx", "counts"]:
                continue
            result_temp[column] = np.interp(objtime_interp["timestamp"], srcdata["timestamp"], srcdata[column])
        # 添加计数列,由于是线性插值,所以计数列的值都是2
        result_temp["counts"] = 2
    else:
        raise ValueError("method参数错误")
    # 为插值失败的数据添加计数列,计数列的值为0
    result = pd.DataFrame(index=objtime.index, columns=result_temp.columns)
    result["counts"] = 0
    result.update(result_temp)
    return result