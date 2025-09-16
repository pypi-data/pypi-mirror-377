import pandas as pd
from swcgeom.core import Tree, Population, Populations
from swcgeom.transforms import ToImageStack
from collections.abc import Iterable
from tifffile import imwrite, imread
import numpy as np
import scipy.ndimage
import tempfile
from pathlib import Path
from typing import Union


# 自定义ToImageStack, 原本ToImageStack保存的tif轴顺序不对
class MyToImageStack(ToImageStack):
    @staticmethod
    def save_tif(
        fname: str,
        frames: Iterable[np.typing.NDArray[np.uint8]],
        resolution: tuple[float, float] = (1, 1),
    ) -> None:
        imwrite(
            fname,
            np.array(list(frames)).swapaxes(1, 2)
        )

# 解析SWC文件
def parse_swc(swc_file):
    df = pd.read_csv(swc_file, sep=' ', header=None)
    df.columns = ['ID', 'Type', 'X', 'Y', 'Z', 'Radius', 'Parent']
    return df

def check_swc_is_multi_root(swc_file):
    swc = parse_swc(swc_file)
    parent = swc['Parent']
    if (parent == -1).sum() > 1:
        return True
    else:
        return False

# 处理SWC文件
# ID从1开始连续编号
# 将丢失父节点的节点父节点设为-1
def swc_process(input_file, save_file):
    swc = parse_swc(input_file)
    id_map = {old_id: new_id for new_id, old_id in enumerate(swc['ID'], start=1)}
    swc['ID'] = swc['ID'].map(id_map)
    swc['Parent'] = swc['Parent'].map(id_map).fillna(-1).astype(int)
    swc.to_csv(save_file, sep=' ', header=False, index=False)
    return save_file


def convert_swc_to_mask(img_file, swc_file, mask_file, save=True, r=None):
    with tempfile.TemporaryDirectory() as tempdir:
        if r is not None:
            swc_df = parse_swc(swc_file)
            swc_df['Radius'] = r  # 重设半径为1
            temp_swc_file = Path(tempdir) / Path(swc_file).name
            swc_df.to_csv(temp_swc_file, sep=' ', header=False, index=False)
            swc_file = temp_swc_file
        if check_swc_is_multi_root(swc_file):
            swc = Population.from_multi_roots_swc(swc_file)
        else:
            swc = Tree.from_swc(swc_file)

    trans = MyToImageStack()

    if save:
        trans.transform_and_save(mask_file, swc, verbose=False, **{'ranges':([0, 0, 0], imread(img_file).shape[::-1])})
        return Path(mask_file).name
    else:
        frames = trans.transform(swc, verbose=False, **{'ranges':([0, 0, 0], imread(img_file).shape[::-1])})
        return np.array(list(frames)).swapaxes(1, 2)
       

def compute_distance_transform(image):
    """
    计算图像的距离变换，返回每个像素到最近白色像素的距离
    """
    return scipy.ndimage.distance_transform_edt(image == 0)  # 计算每个像素到最近前景的距离

# 按照neurolink论文的方式
def distance_function(D_C, d_M):
    """
    使用阈值方法计算距离函数 d(x)，如果 D_C(x) 小于 d_M，则进行线性衰减。
    
    参数：
    - D_C: 欧几里得距离变换（距离到最近神经元节点的距离）
    - d_M: 定义的阈值，通常与邻域大小有关
    
    返回：
    - 距离函数 d(x)
    """
    d = np.zeros_like(D_C)
    mask = D_C < d_M
    d[mask] = 1 - D_C[mask] / d_M  # 线性衰减
    return d

def convert_mask_to_dist(mask, dist_file, s=10, uint8=False):
    if isinstance(mask, Union[str, Path]):
        mask = imread(mask)
    elif isinstance(mask, np.ndarray):
        mask = mask
    else:
        print(type(mask))
        raise ValueError("mask must be a file path or a numpy array")
    
    D_C = compute_distance_transform(mask)
    d_M = s / 2  # 根据论文设置d_M为邻域大小的一半
    dist_map = distance_function(D_C, d_M)
    if uint8:
        dist_map = (dist_map * 255).astype(np.uint8)
    else:
        dist_map = dist_map.astype(np.float32)
    if dist_file is not None:
        imwrite(dist_file, dist_map)
        return dist_file
    else:
        return dist_map

def convert_swc_to_dist(img_file, swc_file, dist_file, s=10, uint8=False):
    mask = convert_swc_to_mask(img_file, swc_file, None, save=False, r=1)
    return convert_mask_to_dist(mask, dist_file, s, uint8)

def convert_nnunet_predict_prob_to_tif(input_file, output_file=None, uint8=True, channel=1):
    data = np.load(input_file)['probabilities'][channel]
    if uint8:
        data = (data * 255).astype(np.uint8)
    else:
        data = data.astype(np.float32)
    if output_file is None:
        return data
    imwrite(output_file, data)
    return Path(output_file).name

