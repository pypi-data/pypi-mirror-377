from muse.data_source.base import DataSourceInterface
from muse.data_source.ds_utils import filter_ports, filter_ports_sec, convert_decimal_to_float, get_all_unique_fields
from muse.muse_config import APP_LOCATE
import polars as pl
import json
import os

class DemoDataSource(DataSourceInterface):
    data_locate = APP_LOCATE + '/data/'

    def get_datasource_name(self):
        return 'Demo用数据源'

    def get_basic_inds(self):
        return ['资产代码', '资产名称', '资产标签', '产品代码', '产品简称', '产品标签', '主体代码', '主体名称', '主体标签', '日期']

    def get_port_tags(self):
        tags = pl.read_excel(self.data_locate + '产品标签列.xlsx')
        return tags.columns

    def get_port_inds(self):
        inds = pl.read_excel(self.data_locate + '产品指标列.xlsx')
        return inds.columns

    def get_asset_tags(self):
        tags = pl.read_excel(self.data_locate + '资产标签列.xlsx')
        return tags.columns

    def get_asset_inds(self):
        inds = pl.read_excel(self.data_locate + '资产指标列.xlsx')
        return inds.columns

    def get_data(self, run_method: str, data_subject: str, sec_ids: list = [], port_ids: list = [], tags: list = [],
                 inds: list = [], start_date=None, end_date=None, penetrate=None):
        if penetrate:
            penetrate = '全穿透'
        else:
            penetrate = '不穿透'
        pdf = None

        if data_subject == '持仓指标':
            asset_df = pl.read_excel(self.data_locate + '资产指标汇总.xlsx', schema_overrides={'日期': pl.Date})
            asset_tags = pl.read_excel(self.data_locate + '资产标签.xlsx')
            asset_df = asset_df.join(asset_tags, on=['资产代码'], how='left')
            pdf = filter_ports_sec(pdf=asset_df, port_ids=port_ids, sec_ids=sec_ids, start_date=start_date,
                                   end_date=end_date)
            # 获得产品代码
            port_ids = pdf.select("产品代码").unique().to_series().to_list()
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx', schema_overrides={'日期': pl.Date})
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            ports = filter_ports(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)
            # 合并资产和产品
            pdf = pdf.join(ports, on=['产品代码', '日期'], how='left')
            pdf = convert_decimal_to_float(pdf)
        elif data_subject == '产品指标':
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx', schema_overrides={'日期': pl.Date})
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            pdf = filter_ports_sec(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)

        merged_cols = tags + inds
        if len(merged_cols) > 0:
            all_cols = get_all_unique_fields(merged_cols, self.get_basic_inds())
            existing_cols = [c for c in all_cols if c in pdf.columns]
            pdf = pdf.select(existing_cols)
        return pdf

    def get_repository_inds(self, run_method: str, repository: str, ind_list: list, params: dict):
        # 处理指标列表
        port_tags = params.get('PORT_TAGS', None)
        asset_tags = params.get('SEC_TAGS', None)
        start_date = params.get('START_DATE', None)
        end_date = params.get('END_DATE', None)
        port_ids = params.get('PORT_IDS', None)
        if port_ids and isinstance(port_ids, str):
            port_ids = [p.strip() for p in port_ids.split(',')]
        elif port_ids and isinstance(port_ids, list):
            pass
        else:
            port_ids = []
        sec_ids = params.get('sec_ids', None)
        if sec_ids and isinstance(sec_ids, str):
            sec_ids = [p.strip() for p in sec_ids.split(',')]
        elif port_ids and isinstance(port_ids, list):
            pass
        else:
            sec_ids = []
        # 读取指标库
        rep_locate = f'{self.data_locate}指标库/{repository}.xlsx'
        # 选择合适的指标
        df = pl.read_excel(rep_locate, schema_overrides={'日期': pl.Date})
        if len(ind_list) > 0:
            existing_cols = [col for col in set(self.get_basic_inds() + ind_list) if col in df.columns]
            df = df.select(existing_cols)
        # 过滤产品代码、资产代码和日期区间
        df = filter_ports_sec(df, port_ids, sec_ids, start_date, end_date)
        # 处理产品标签
        if port_tags:
            if isinstance(port_tags, str):
                port_tags = [p.strip() for p in port_tags.split(',')]
            # 检查标签是否存在
            valid_port_tags = []
            for tag in port_tags:
                if tag in self.get_port_tags():
                    valid_port_tags.append(tag)
            if not valid_port_tags and len(valid_port_tags) == 0:
                raise ValueError(f"产品标签 {port_tags} 不在数据列中！")
            p_tags = pl.read_excel(f'{self.data_locate}产品标签.xlsx')
            p_tags = p_tags.select(['产品代码'] + valid_port_tags)
            df = df.join(p_tags, on=['产品代码'], how='left')
            # 动态构建 OR 条件
            port_condition = pl.any_horizontal(
                *[pl.col(tag) == "是" for tag in valid_port_tags]
            )
            df = df.filter(port_condition)
        # 处理资产标签
        if asset_tags:
            if isinstance(asset_tags, str):
                asset_tags = [p.strip() for p in asset_tags.split(',')]
            # 检查标签是否存在
            valid_asset_tags = []
            for tag in asset_tags:
                if tag in self.get_asset_tags():
                    valid_asset_tags.append(tag)

            if not valid_asset_tags and len(valid_asset_tags) == 0:
                raise ValueError(f"资产标签 {asset_tags} 不在数据列中！")
            # 动态构建 OR 条件
            a_tags = pl.read_excel(f'{self.data_locate}资产标签.xlsx')
            a_tags = a_tags.select(['资产代码'] + valid_asset_tags)
            df = df.join(a_tags, on=['资产代码'], how='left')
            asset_condition = pl.any_horizontal(
                *[pl.col(tag) == "是" for tag in valid_asset_tags]
            )
            df = df.filter(asset_condition)
        return df

    def _gen_repository_meta(self):
        meta = list()
        directory = self.data_locate + '指标库/'
        if not os.path.exists(directory):
            print(f"错误：目录 '{directory}' 不存在")
            return meta

            # 遍历目录及其子目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 检查文件后缀是否为.xlsx
                if file.endswith('.xlsx'):
                    dd = dict()
                    # 获取文件的绝对路径并添加到列表中
                    full_path = os.path.join(root, file)
                    rep = file.split('.')[0]
                    dd['指标库名称'] = rep
                    dd['指标库描述'] = rep
                    param = {
                        'PORT_IDS': {'参数描述': '产品代码', '参数类型': 'String(逗号分隔的产品代码)', '参数必填': '否',
                                     '参数默认值': ''},
                        'PORT_TAGS': {'参数描述': '产品类型标签', '参数类型': 'String(逗号分隔的产品类型)',
                                      '参数必填': '否', '参数默认值': ''},
                        'START_DATE': {'参数描述': '数据开始日期', '参数类型': 'String(YYYY-MM-DD)', '参数必填': '是',
                                       '参数默认值': ''},
                        'END_DATE': {'参数描述': '数据结束日期', '参数类型': 'String(YYYY-MM-DD)', '参数必填': '是',
                                     '参数默认值': ''}
                        }
                    dd['参数列表'] = param
                    df = pl.read_excel(full_path)
                    dd['指标列表'] = [{'指标名称': col, '指标描述': col} for col in list(df.columns)]
                    meta.append(dd)
        with open(self.data_locate + '指标库/rep_orin.json', 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
        return meta

    def get_all_repository_metadata(self):
        # self._gen_repository_meta()
        with open(self.data_locate + '指标库/rep.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return meta

    def get_repository_params(self, rep_list: list):
        {'apiParamCode': 'PORT_IDS', 'apiParamName': '产品代码\t', 'apiParamDesc': '', 'apiParamType': 'String',
         'apiParamDict': None, 'apiParamRequired': True, 'defaultValue': '0800099C91,0800099C93'}
        meta_all = self.get_all_repository_metadata()
        param = list()
        for m in meta_all:
            if m['指标库名称'] in rep_list:
                for p_name, p in m['参数列表'].items():
                    dd = dict()
                    dd['apiParamCode'] = p_name
                    dd['apiParamName'] = p['参数描述']
                    dd['apiParamType'] = 'String'
                    dd['apiParamDict'] = None
                    dd['apiParamRequired'] = True if p['参数必填'] == '是' else False
                    dd['defaultValue'] = p['参数默认值']
                    param.append(dd)
        return param


    def get_repository_metadata(self, rep_list: list):
        meta_all = self.get_all_repository_metadata()
        meta = list()
        for m in meta_all:
            if m['指标库名称'] in rep_list:
                meta.append(m)
        return meta

if __name__ == '__main__':
    ds = DemoDataSource()
    print(ds.get_port_tags())
    print(ds.get_port_inds())
    print(ds.get_asset_tags())
    print(ds.get_asset_inds())
    print(ds.get_all_repository_metadata())
    print(ds.get_repository_metadata(['产品估值', '产品风险']))
    print(ds.get_repository_params(['产品估值', '产品风险']))