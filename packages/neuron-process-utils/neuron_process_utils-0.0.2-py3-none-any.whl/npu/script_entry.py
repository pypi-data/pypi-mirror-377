import multiprocessing
import argparse
from npu.utils import swc_process, convert_swc_to_mask, convert_mask_to_dist, convert_swc_to_dist, convert_nnunet_predict_prob_to_tif
from pathlib import Path
from tqdm import tqdm

def swc_process_entry():
    args = argparse.ArgumentParser(description='swc处理脚本, 用于reindex swc文件, ID从1开始连续编号, 丢失父节点的节点父节点设为-1')
    args.add_argument('--input', '-i', type=str, required=True, help='input swc directory')
    args.add_argument('--output', '-o', type=str, help='output swc directory')
    args.add_argument('--np', type=int, default=8, help='number of processes')
    args = args.parse_args()

    args.output = args.output if args.output is not None else args.input

    swc_file_list = list(Path(args.input).glob('*.swc'))
    Path(args.output).mkdir(exist_ok=True)

    r = []
    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        for swc_file in swc_file_list:
            output_file = Path(args.output) / swc_file.name
            r.append(
                p.starmap_async(
                    swc_process,
                    ((
                        swc_file,
                        output_file
                    ),)
                )
            )

        pbar = tqdm(r)
        for i in pbar:
            name = i.get()[0]
            pbar.set_description(f'Processing {name}')

def swc_to_mask_entry():
    args = argparse.ArgumentParser(description='swc转mask脚本')
    args.add_argument('--image', '-i', type=str, required=True, help='input img directory')
    args.add_argument('--swc', '-s', type=str, required=True, help='input swc directory')
    args.add_argument('--output', '-o', type=str, required=True, help='output mask directory')
    args.add_argument('--np', type=int, default=8, help='number of processes')
    args.add_argument('--radius', '-r', type=float, default=None, help='重设swc半径为多少, 仅在reset_r时有效')
    args = args.parse_args()

    img_file_list = list(Path(args.image).glob('*.tif'))
    swc_file_list = [Path(args.swc) / f.with_suffix('.swc').name for f in img_file_list]
    mask_file_list = [Path(args.output) / f.with_suffix('.tif').name for f in img_file_list]
    Path(args.output).mkdir(exist_ok=True)  

    r = []
    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        for img_file, swc_file, mask_file in zip(img_file_list, swc_file_list, mask_file_list):
            r.append(
                p.starmap_async(
                    convert_swc_to_mask,
                    ((
                        img_file,
                        swc_file,
                        mask_file,
                        True,
                        args.radius
                    ),)
                )
            )

        pbar = tqdm(r)
        for i in pbar:
            name = i.get()[0]
            pbar.set_description(f'Processing {name}')

def swc_to_dist_entry():
    args = argparse.ArgumentParser(description='swc转dist脚本')
    args.add_argument('--image', '-i', type=str, required=True, help='input img directory')
    args.add_argument('--swc', '-s', type=str, required=True, help='input swc directory')
    args.add_argument('--output', '-o', type=str, required=True, help='output mask directory')
    args.add_argument('--np', type=int, default=8, help='number of processes')
    args.add_argument('--lns', type=float, default=10, help='local neighborhoods size')
    args.add_argument('--s', action='store_true', help='scale distmap to [0, 255] and save as uint8')
    args = args.parse_args()

    img_file_list = list(Path(args.image).glob('*.tif'))
    swc_file_list = [Path(args.swc) / f.with_suffix('.swc').name for f in img_file_list]
    dist_file_list = [Path(args.output) / f.with_suffix('.tif').name for f in img_file_list]
    Path(args.output).mkdir(exist_ok=True)

    r = []
    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        for img_file, swc_file, dist_file in zip(img_file_list, swc_file_list, dist_file_list):
            r.append(
                p.starmap_async(
                    convert_swc_to_dist,
                    ((
                        img_file,
                        swc_file,
                        dist_file,
                        args.lns,
                        args.s
                    ),)
                )
            )

        pbar = tqdm(r)
        for i in pbar:
            name = i.get()[0]
            pbar.set_description(f'Processing {name}')


def mask_to_dist_entry():
    args = argparse.ArgumentParser(description='mask转dist脚本')
    args.add_argument('--mask', '-m', type=str, required=True, help='input mask directory')
    args.add_argument('--output', '-o', type=str, required=True, help='output dist directory')
    args.add_argument('--np', type=int, default=8, help='number of processes')
    args.add_argument('--lns', type=float, default=10, help='local neighborhoods size')
    args.add_argument('--s', action='store_true', help='scale distmap to [0, 255] and save as uint8')
    args = args.parse_args()

    mask_file_list = list(Path(args.mask).glob('*.tif'))
    dist_file_list = [Path(args.output) / f.with_suffix('.tif').name for f in mask_file_list]
    Path(args.output).mkdir(exist_ok=True)

    r = []
    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        for mask_file, dist_file in zip(mask_file_list, dist_file_list):
            r.append(
                p.starmap_async(
                    convert_mask_to_dist,
                    ((
                        mask_file,
                        dist_file,
                        args.lns,
                        args.s
                    ),)
                )
            )

        pbar = tqdm(r)
        for i in pbar:
            name = i.get()[0]
            pbar.set_description(f'Processing {name}')

def nnunet_predict_prob_to_tif_entry():
    args = argparse.ArgumentParser(description='nnUNet预测结果概率图转tif脚本')
    args.add_argument('--input', '-i', type=str, required=True, help='input npy directory')
    args.add_argument('--output', '-o', type=str, help='output tif directory')
    args.add_argument('--np', type=int, default=8, help='number of processes')
    args.add_argument('--uint8', action='store_true', help='scale to [0, 255] and save as uint8')
    args.add_argument('--channel', '-c', type=int, default=1, help='which channel to save, 0-based index')
    args = args.parse_args()

    if args.output is None:
        args.output = args.input

    input_file_list = list(Path(args.input).glob('*.npz'))
    output_file_list = [Path(args.output) / (f.stem + '_probabilities.tif') for f in input_file_list]
    Path(args.output).mkdir(exist_ok=True)

    r = []
    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        for input_file, output_file in zip(input_file_list, output_file_list):
            r.append(
                p.starmap_async(
                    convert_nnunet_predict_prob_to_tif,
                    ((
                        input_file,
                        output_file,
                        args.uint8,
                        args.channel
                    ),)
                )
            )

        pbar = tqdm(r)
        for i in pbar:
            name = i.get()[0]
            pbar.set_description(f'Processing {name}')