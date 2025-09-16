demos = list()

demo1 = '''
产品基本信息 = 指标('产品基本信息（时点）', ['产品代码', '产品简称'], {'PORT_TAGS': ['现金管理类产品'], 'START_DATE': '2023-03-01', 'END_DATE': '2023-03-01'})
'''
demo2 = '''
产品估值数据 = 指标('产品估值（时序）', ['产品代码', '统计日期', '总资产', '净资产'], {'PORT_TAGS': '现金管理类产品', 'START_DATE': '2023-03-01', 'END_DATE': '2024-03-01'})
'''
demo3 = '''
产品估值数据 = 指标('产品投资人（时序）', ['产品代码', '统计日期', '总份额', '前10大客户份额占比'], {'PORT_TAGS': ['现金管理类'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-06-17'})
'''
demo4 = '''
产品估值数据 = 指标('大类资产占比（时序）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-06-17'})
'''
demo5 = '''
产品估值数据 = 指标('申赎信息（时序）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-12', 'LOOP_DAYS': 30, 'METHOD': 'MAX'})
'''
demo6 = '''
产品估值数据 = 指标('资产基本信息（时点）', [], {'SEC_TAGS': ['信用债'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02'})
'''
demo7 = '''
产品估值数据 = 指标('持仓指标（新）', ['产品代码', '资产代码', '有效日期', '全价市值'], {'PORT_TAGS': ['现金管理类产品'], 'START_DATE': '2023-03-10', 'END_DATE': '2023-03-10', 'PENETRATE_TYPE': '01'})
'''
demo8 = '''
资产期间收益 = 指标('资产收益率（时序）', [], {'PORT_TAGS': ['现金管理类产品'], 'SEC_TAGS': ['资产管理产品', '企业债券', '信用债'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-04'})
'''
demo9 = '''
资产期间收益 = 指标('累计单利收益率', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02'})
'''
demo10 = '''
资产期间收益 = 指标('复权复利收益率', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02'})
'''
demo11 = '''
资产期间收益 = 指标('基准收益率', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02'})
'''
demo12 = '''
资产期间收益 = 指标('产品期间收益（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2023-03-01', 'END_DATE': '2023-03-15', 'BENCHMARK_ID': '', 'BENCHMARK_TYPE': '03'})
'''
demo13 = '''
资产期间收益 = 指标('产品费前收益率（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-04', 'BENCHMARK_ID': '000300.SH', 'BENCHMARK_TYPE': '03'})
'''
demo14 = '''
资产期间收益 = 指标('产品期间收益时点指标库', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02'})
'''
demo15 = '''
资产期间收益 = 指标('风险调整后收益（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-31', 'BENCHMARK_TYPE': '03'})
'''
demo16 = '''
资产期间收益 = 指标('产品每日收益（时序）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-31', 'BENCHMARK_TYPE': '03'})
'''
demo17 = '''
资产期间收益 = 指标('收益分解(产品)（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-04', 'PENETRATE_TYPE': '01'})
'''
# 下面这个有问题
demo18 = '''
资产期间收益 = 指标('收益分解(全维度)', [], {'PORT_TAGS': ['公募产品', '混合类产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-06-30', 'V_DATE': '2022-01-01', 'AGG': 'False', 'METHOD': 'CF'})
'''
demo19 = '''
资产期间收益 = 指标('产品收益（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-04', 'BENCHMARK_ID': '000300.SH', 'BENCHMARK_TYPE': '03'})
'''
demo20 = '''
资产期间收益 = 指标('产品内部基准收益', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-04'})
'''
demo21 = '''
资产期间收益 = 指标('产品期间收益率（时段）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-05-02', 'BENCHMARK_TYPE': '03'})
'''
demo22 = '''
资产期间收益 = 指标('产品Campisi归因', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2023-03-01', 'END_DATE': '2023-03-31', 'ABS': 'False'})
'''
demo23 = '''
资产期间收益 = 指标('市场风险（时序）', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-06-04'})
'''
demo24 = '''
资产期间收益 = 指标('产品VaR', [], {'PORT_TAGS': ['公募产品', '混合类产品'], 'START_DATE': '2022-05-02', 'END_DATE': '2022-06-04'})
'''
demo25 = '''
资产期间收益 = 指标('产品ECL', [], {'PORT_TAGS': ['开放式公募产品', '混合类产品'], 'DATA_DATE': '2023-03-31'})
'''
demo26 = '''
资产期间收益 = 指标('利率风险(产品)（时点）', [], {'PORT_TAGS': ['公募产品', '混合类产品'], 'START_DATE': '2023-03-01', 'END_DATE': '2023-03-05'})
'''
demo27 = '''
资产期间收益 = 指标('损益分析', [], {'PORT_TAGS': ['开放式公募产品'], 'START_DATE': '2023-03-01', 'END_DATE': '2023-03-31'})
'''
# 将所有demo添加到demos数组中
demos.append(demo1)
demos.append(demo2)
demos.append(demo3)
demos.append(demo4)
demos.append(demo5)
demos.append(demo6)
demos.append(demo7)
demos.append(demo8)
demos.append(demo9)
demos.append(demo10)
demos.append(demo11)
demos.append(demo12)
demos.append(demo13)
demos.append(demo14)
demos.append(demo15)
demos.append(demo16)
demos.append(demo17)
demos.append(demo18)
demos.append(demo19)
demos.append(demo20)
demos.append(demo21)
demos.append(demo22)
demos.append(demo23)
demos.append(demo24)
demos.append(demo25)
demos.append(demo26)
demos.append(demo27)
def get_demos():
    return demos