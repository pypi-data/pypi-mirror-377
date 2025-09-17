from enum import Enum

class KaqCommsionRateRedisPrefixEnum(Enum):
    binance_future = 'kaq_binance_future_commsion_rate_'
    bybit_future = 'kaq_bybit_future_commsion_rate_'
    okx_future = 'kaq_okx_future_commsion_rate_'
    bitget_future = 'kaq_bitget_future_commsion_rate_'
    gate_future = 'kaq_gate_future_commsion_rate_'
    htx_future = 'kaq_gate_future_commsion_rate_'
    
    binance_spot = 'kaq_binance_spot_commsion_rate_'
    bybit_spot = 'kaq_bybit_spot_commsion_rate_'
    okx_spot = 'kaq_okx_spot_commsion_rate_'
    bitget_spot = 'kaq_bitget_spot_commsion_rate_'
    gate_spot = 'kaq_gate_spot_commsion_rate_'
    htx_spot = 'kaq_htx_spot_commsion_rate_'

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