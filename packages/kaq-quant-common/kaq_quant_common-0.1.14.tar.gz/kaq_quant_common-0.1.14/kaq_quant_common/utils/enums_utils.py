from enum import Enum

class KaqCommsionRateRedisPrefixEnum(Enum):
    binance = 'kaq_binance_commsion_rate_'
    bybit = 'kaq_bybit_commsion_rate_'
    okx = 'kaq_okx_commsion_rate_'
    bitget = 'kaq_bitget_commsion_rate_'
    gate = 'kaq_gate_commsion_rate_'

class KaqCoinDataEnum(Enum):
    '''
    枚举检测
    '''
    klines = 'klines' # klines
    global_long_short_account_ratio = 'global_long_short_account_ratio' # 多空持仓人数比
    open_interest_hist = 'open_interest_hist' # 合约持仓量历史
    taker_long_short_ratio = 'taker_long_short_ratio' # 合约主动买卖量
    top_long_short_account_ratio = 'top_long_short_account_ratio' # 大户账户数多空比
    top_long_short_position_ratio = 'top_long_short_position_ratio' # 大户持仓量多空比