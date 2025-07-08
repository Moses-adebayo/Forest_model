import numpy as np

def calculate_nse(obs, sim_obs):
    """
    计算纳什效率系数（NSE）

    参数:
        obs (array-like): 观测数据
        sim_obs (array-like): 模拟数据，必须与 obs 长度一致

    返回:
        float: NSE 值
    """
    obs = np.asarray(obs)
    sim_obs = np.asarray(sim_obs)

    # 检查长度一致
    if obs.shape != sim_obs.shape:
        raise ValueError("obs 和 sim_obs 必须具有相同的形状")

    numerator = np.sum((obs - sim_obs) ** 2)
    denominator = np.sum((obs - np.mean(obs)) ** 2)

    if denominator == 0:
        return np.nan  # 避免除以零的情况

    nse = 1 - (numerator / denominator)
    return nse
