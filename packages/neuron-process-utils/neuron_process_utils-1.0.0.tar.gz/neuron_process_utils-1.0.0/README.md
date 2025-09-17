# 神经元数据处理工具
注：需要图像和swc文件同名，例如(1.tif, 1.swc)
```shell
# 处理swc，将parent指向节点不存在于swc文件中的值置为-1，对swc进行reindex
# 保存到原目录
npu_swc_process -i ./CWMBS/swc
# 保存到新目录
npu_swc_process -i ./CWMBS/swc -o ./CWMBS/process_swc

# swc转mask，根据xyz和r，将xyz点r范围内的像素设为255
npu_swc_to_mask -i ./CWMBS/img -s ./CWMBS/process_swc -o ./CWMBS/process_mask 
# 重设半径
npu_swc_to_mask -i ./CWMBS/img -s ./CWMBS/process_swc -o ./CWMBS/process_mask -r 1

# swc转dist(需要swc转为mask时的r为1)，以0-1 float32存储
npu_swc_to_dist -m ./CWMBS/img -s ./CWMBS/process_swc -o ./CWMBS/process_dist
# 设置邻域范围
npu_swc_to_dist -m ./CWMBS/img -s ./CWMBS/process_swc -o ./CWMBS/process_dist --lns 10
# 以0-255 uint8存储
npu_swc_to_dist -m ./CWMBS/img -s ./CWMBS/process_swc -o ./CWMBS/process_dist --s

# mask转dist(需要swc转为mask时的r为1)，以0-1 float32存储
npu_mask_to_dist -m ./CWMBS/process_mask -o ./CWMBS/process_dist
# 设置邻域范围
npu_mask_to_dist -m ./CWMBS/process_mask -o ./CWMBS/process_dist --lns 10
# 以0-255 uint8存储
npu_mask_to_dist -m ./CWMBS/process_mask -o ./CWMBS/process_dist --s
```