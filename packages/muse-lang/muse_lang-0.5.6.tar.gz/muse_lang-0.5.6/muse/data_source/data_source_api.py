from muse.data_source.base import DataSourceInterface
from muse.data_source.ds_utils import filter_ports, filter_ports_sec, convert_decimal_to_float, get_all_unique_fields
import polars as pl
import os
from muse.utils.jx_http_request import JxHttpClient
from collections import OrderedDict
from muse.muse_config import DATA_PATH, MID_BASE_URL, ASSET_TAG_GROUP, PORT_TAG_GROUP, REPOSITORY_GROUP

class DataSourceApi(DataSourceInterface):
    def get_datasource_name(self):
        return f'指标库数据源 - 地址: {MID_BASE_URL}'

    def get_basic_inds(self):
        return ['资产代码', '资产名称', '资产标签', '产品代码', '产品简称', '产品标签', '主体代码', '主体名称', '主体标签', '日期']

    def get_port_tags(self):
        # tags = pl.read_excel(self.data_locate + '产品标签列.xlsx')
        jxClient = JxHttpClient(MID_BASE_URL)
        port_targs_params = {
            "classCode": 80,
            "grpName": "限额指标产品标签组",
            "curUser": {
                "realName": "系统管理员",
                "userName": "padmin",
                "orgCode": "BM0008"
            }
        }
        rst = jxClient.post("/labelSystem/getLabelCloud", data=port_targs_params)
        rst_list = [item['typeName'] for item in rst if item['count'] > 0]
        return rst_list

    def get_port_inds(self):
        inds = pl.read_excel(DATA_PATH + '/产品指标列.xlsx')
        return inds.columns

    def get_asset_tags(self):
        jxClient = JxHttpClient(MID_BASE_URL)
        port_targs_params = {
            "classCode": 81,
            "grpName": ASSET_TAG_GROUP,
            "curUser": {
                "realName": "系统管理员",
                "userName": "padmin",
                "orgCode": "BM0008"
            }
        }
        rst = jxClient.post("/labelSystem/getLabelCloud", data=port_targs_params)
        rst_list = [item['typeName'] for item in rst if item['count'] > 0]
        return rst_list

    def get_asset_inds(self):
        inds = pl.read_excel(DATA_PATH + '/资产指标列.xlsx')
        return inds.columns

    def get_data(self, run_method: str, data_subject: str, sec_ids: list = [], port_ids: list = [], tags: list = [],
                 inds: list = [], start_date=None, end_date=None, penetrate=None):
        if penetrate:
            penetrate = '全穿透'
        else:
            penetrate = '不穿透'
        pdf = None

        if data_subject == '持仓指标':
            asset_df = pl.read_excel(DATA_PATH + '/资产指标汇总.xlsx')
            asset_tags = pl.read_excel(DATA_PATH + '/资产标签.xlsx')
            asset_df = asset_df.join(asset_tags, on=['资产代码'], how='left')
            pdf = filter_ports_sec(pdf=asset_df, port_ids=port_ids, sec_ids=sec_ids, start_date=start_date,
                                   end_date=end_date)
            # 获得产品代码
            port_ids = pdf.select("产品代码").unique().to_series().to_list()
            ports = pl.read_excel(DATA_PATH + '/产品指标汇总.xlsx')
            port_tags = pl.read_excel(DATA_PATH + '/产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            ports = filter_ports(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)
            # 合并资产和产品
            pdf = pdf.join(ports, on=['产品代码', '日期'], how='left')
            pdf = convert_decimal_to_float(pdf)
        elif data_subject == '产品指标':
            ports = pl.read_excel(self.data_locate + '/产品指标汇总.xlsx')
            port_tags = pl.read_excel(self.data_locate + '/产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            pdf = filter_ports_sec(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)

        merged_cols = tags + inds
        if len(merged_cols) > 0:
            all_cols = get_all_unique_fields(merged_cols, self.get_basic_inds())
            existing_cols = [c for c in all_cols if c in pdf.columns]
            pdf = pdf.select(existing_cols)
        return pdf

    # 根据标签获取id列表
    def get_ids_by_tags(self, tags: list = [], tag_grps = []):
        tag_grps_list = [PORT_TAG_GROUP, ASSET_TAG_GROUP]
        if tag_grps:
            tag_grps_list = tag_grps

        api_params = {
            "grpNames": tag_grps_list,
            "labelNames": tags
        }
        jxClient = JxHttpClient(MID_BASE_URL)
        rst = jxClient.post("/labelSystem/getIdsByLabelName", data=api_params)
        return rst

    def get_repository_inds(self, run_method: str, repository: str, ind_list: list, params: dict):
        # 基础API参数
        api_params = {
            "resource": repository,
            "paramMaps": {"SYS_ID": ""},
            "ind_name_list": ind_list,
            "pageSize": 1000000,
            "pageNum": 1,
            "curUser": {"userName": "test001"}
        }

        # 处理日期参数, 如果传入了小写的，则转成大写
        date_mapping = {
            'start_date': 'START_DATE',
            'end_date': ['END_DATE', 'DATA_DATE']
        }

        for src_key, dest_keys in date_mapping.items():
            if src_key in params:
                value = params.pop(src_key)
                if value:
                    # 统一将目标键转换为列表处理
                    target_keys = dest_keys if isinstance(dest_keys, list) else [dest_keys]
                    for target_key in target_keys:
                        params[target_key] = value

        ### ---------- 处理 port_ids ---------- 开始
        port_ids = []
        if 'port_ids' in params:
            port_ids_param = params.pop('port_ids', '')
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(port_ids_param, str):
                port_ids = [item.strip() for item in port_ids_param.split(',') if item.strip()]
            elif isinstance(port_ids_param, list):
                port_ids = port_ids_param

        # 再处理 port_tags
        if 'PORT_TAGS' in params:
            port_tags = params.pop('PORT_TAGS')  # 使用 pop 移除参数
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(port_tags, str):
                port_tags = [tag.strip() for tag in port_tags.split(',') if tag.strip()]

            if isinstance(port_tags, list) and port_tags:
                port_tags_ids = self.get_ids_by_tags(tags=port_tags)
                # 合并并去重
                if port_tags_ids:
                    port_ids = list(set(port_ids + port_tags_ids))

        if port_ids:
            params['PORT_IDS'] = ",".join(port_ids)
        ### ---------- 处理 port_ids ---------- 结束

        ### ---------- 处理 sec_ids ---------- 开始
        sec_ids = []
        if 'SEC_IDS' in params:
            sec_ids_param = params.pop('sec_ids', '')
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(sec_ids_param, str):
                sec_ids = [item.strip() for item in sec_ids_param.split(',') if item.strip()]
            elif isinstance(sec_ids_param, list):
                sec_ids = sec_ids_param

        if 'SEC_TAGS' in params:
            sec_tags = params.pop('SEC_TAGS')  # 使用 pop 移除参数
            # 处理逗号分隔的字符串，转换为列表
            if isinstance(sec_tags, str):
                sec_tags = [tag.strip() for tag in sec_tags.split(',') if tag.strip()]

            if isinstance(sec_tags, list) and sec_tags:
                sec_tags_ids = self.get_ids_by_tags(tags=sec_tags)
                if sec_tags_ids:
                    sec_ids = list(set(sec_ids + sec_tags_ids))

        if sec_ids:
            params['SEC_IDS'] = ",".join(sec_ids)
        ### ---------- 处理 sec_ids ---------- 结束

        api_params["paramMaps"] = {**api_params["paramMaps"], **params}
        jxClient = JxHttpClient(MID_BASE_URL)
        rst = jxClient.post("/xlsApiPlugin/museLoadData", data=api_params)
        # 提取列名
        column_names = [header['ind_name'] for header in rst['headers']]

        df = create_dataframe_safely(rst['datas'], column_names)
        return df

    def get_repository_metadata(self, rep_list: list):
        rep_locate = f'{DATA_PATH}/指标库/{rep_list[0]}.xlsx'
        if not os.path.exists(rep_locate):
            return {}
        # 选择合适的指标
        metadata = dict()
        metadata['指标库名称'] = rep_list[0]

        df = pl.read_excel(rep_locate)
        # 指标描述需要额外获取，描述应包含所有枚举值信息; 指标类型信息
        ind_list = [{'指标名称': ind, '指标描述': ind, '指标类型': 'string'} for ind in df.columns]
        metadata['指标列表'] = ind_list
        # 每个指标库都应该一样的部分
        params = {
                    'port_ids': {'参数描述': '产品代码列表', '参数类型': 'list'},
                    'port_tags': {'参数描述': '产品标签列表', '参数类型': 'list'},
                    'asset_tags': {'参数描述': '资产标签列表', '参数类型':'list'},
                    'start_date': {'参数描述': '查询开始日期', '参数类型': 'date'},
                    'end_date': {'参数描述': '查询结束日期', '参数类型': 'data'}
                  }
        # 每个指标库不一样的部分放到下面填补
        metadata['参数列表'] = params
        return metadata


    def get_all_repository_metadata(self):
        jxClient = JxHttpClient(MID_BASE_URL)
        original_data_list = jxClient.get(f"/museapi/loadMuseInds?topics={REPOSITORY_GROUP}")

        if not original_data_list:
            return []  # 如果没有数据，返回空列表

        transformed_data_list = []  # 存储所有转换后的指标库

        # 循环处理每一个指标库
        for original_data in original_data_list:
            transformed_data = OrderedDict()

            # 转换基本信息
            transformed_data['指标库名称'] = original_data['apiName']
            transformed_data['指标库描述'] = original_data['apiDesc']

            # 转换参数列表
            transformed_data['参数列表'] = {}
            for param_key, param_value in original_data['apiParamMap'].items():
                transformed_param = {
                    '参数描述': param_value['apiParamName'],
                    '参数类型': param_value['apiParamType'],
                    '参数必填': '是' if param_value['apiParamRequired'] else '否',
                    '参数默认值': param_value['defaultValue'],
                    '参数字典值(key: 参数含义 Value: 调用时应填值)': param_value['apiParamDict'] if param_value[
                        'apiParamDict'] else '无'
                }
                transformed_data['参数列表'][param_key] = transformed_param

            if 'PORT_IDS' in transformed_data['参数列表']:
                PORT_TAGS_PARAMS = {
                    '参数描述': '逗号分隔的产品标签列表',
                    '参数类型': 'String'
                }
                transformed_data['参数列表']['PORT_TAGS'] = PORT_TAGS_PARAMS

            if 'SEC_IDS' in transformed_data['参数列表']:
                SEC_TAGS_PARAMS = {
                    '参数描述': '逗号分隔的资产标签列表',
                    '参数类型': 'String'
                }
                transformed_data['参数列表']['SEC_TAGS'] = SEC_TAGS_PARAMS

            # 转换指标列表
            transformed_data['指标列表'] = []
            for indicator in original_data['indList']:
                ind_name = indicator['indName']
                ind_desc = indicator['indDesc']
                if ind_name == '产品代码':
                    ind_desc = '理财产品的系统唯一标识码，指标库重要关联指标'
                elif ind_name == '资产代码' or ind_name == '证券代码':
                    ind_desc = '理财产品投资的金融资产的系统唯一标识码, 指标库重要关联指标'
                elif '日期' in ind_name:
                    ind_desc = '表示数据统计日期, 指标库重要关联指标。数据表示为YYYY-mm-dd的日期字符串'

                transformed_indicator = {
                    '指标名称': ind_name,
                    '指标描述': ind_desc
                }
                transformed_data['指标列表'].append(transformed_indicator)

            transformed_data_list.append(transformed_data)

        return transformed_data_list  # 返回转换后的列表

    def get_repository_params(self, rep_list: list):
        jxClient = JxHttpClient(MID_BASE_URL)
        params = jxClient.get(f"/museapi/getApiParamListByApiCodes?apiCodes={','.join(rep_list)}")
        return params


def create_dataframe_safely(data, schema):
    """安全创建DataFrame，处理混合数据类型问题"""
    # 方法1：先尝试正常创建
    try:
        return pl.DataFrame(data, schema=schema, orient='row', infer_schema_length=10000)
    except Exception as e:
        print(f"方法1失败: {e}")

    # 方法2：逐列构建
    data_dict = {}
    for col_idx, col_name in enumerate(schema):
        col_data = []
        for row in data:
            if col_idx < len(row):
                value = row[col_idx]
                # 统一数值类型
                if isinstance(value, (int, float)):
                    col_data.append(float(value))
                else:
                    col_data.append(value)
            else:
                col_data.append(None)
        data_dict[col_name] = col_data

    return pl.DataFrame(data_dict)

if __name__ == '__main__':
    ds = DataSourceApi()
    params={
        "START_DATE": "2023-03-01",
        "END_DATE": "2023-04-05",
        "PORT_TAGS": "现金管理类产品"
    }
    print(ds.get_repository_inds(run_method='', repository='产品估值（时序）', ind_list=['产品代码', '统计日期', '总资产', '净资产'], params=params))
    print(ds.get_repository_inds(run_method='', repository='产品期间收益时点指标库', ind_list=[], params=params))
    print(ds.get_all_repository_metadata())
    print(ds.get_asset_tags())
    print(ds.get_asset_inds())
    print(ds.get_port_tags())
    print(ds.get_port_inds())