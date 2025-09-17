import pathlib
import os
# MUSE所至目录
APP_LOCATE = str(pathlib.Path(os.path.abspath(__file__)).parent)
# 本地文件地址
DATA_PATH = APP_LOCATE + '/data'
# 数据中台地址
MID_BASE_URL = "http://jixunet.top/jxdm_zyrisk"
# 数据中台资产标签组名称
ASSET_TAG_GROUP = "压测标签组"
# 数据中台产品标签组名称
PORT_TAG_GROUP = "限额指标产品标签组"
# 数据中台指标库父级名称，可使用逗号表示多个开放的指标库
REPOSITORY_GROUP = "API指标库"