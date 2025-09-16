import os
import yaml
import pkgutil
import importlib.resources as resources
from loguru import logger


def read_config(pkg_name='kaq_quant_common'):
    config_path = pkgutil.get_data(pkg_name, f'config{os.sep}config.yaml')
    data = yaml.load(config_path, Loader=yaml.FullLoader)
    return data

def get_spot_list(pkg_name='kaq_quant_common'):
    '''
    获取合约对应的现货列表
    '''
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'spot_list' not in data:
        return None
    return data["spot_list"]

def get_future_list(pkg_name='kaq_quant_common'):
    '''
    获取合约的symbol列表
    '''
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'future_list' not in data:
        return None
    return data["future_list"]

def get_api_key_secret(pkg_name='kaq_quant_common'):
    '''
    获取bianace的api_key
    '''
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'api_key' not in data or 'api_secret' not in data:
        return None
    return data["api_key"], data["api_secret"]

def get_proxies(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'proxies' not in data:
        return None
    return data["proxies"]

def get_mysql_info(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'mysql' not in data:
        return None
    data = data['mysql']
    return data["host"], data["port"], data["user"], data["passwd"], data["database"], data["charset"]

def get_redis_info(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'redis' not in data:
        return None
    data = data['redis']
    return data["host"], data["port"], data["passwd"]

def get_posgresql_info(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'posgresql' not in data:
        return None
    data = data['posgresql']
    return data["host"], data["port"], data["user"], data["passwd"], data["database"], data["charset"]

def get_mysql_table_prefix(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'mysql_table_prefix' not in data:
        return None
    data = data['mysql_table_prefix']
    return data

def get_ddb_info(pkg_name='kaq_quant_common'):
    data = read_config(pkg_name)
    if data is None or 'kaq' not in data:
        return None
    data = data['kaq']
    if 'ddb' not in data:
        return None
    data = data['ddb']
    return data["host"], data["port"], data["user"], data["passwd"]


def get_pkg_file(pkg=None, file_name=''):
    if pkg is None:
        logger.error('yml_utils.get_pkg_script pkg is None')
        return None
    '''
    读取文件
    '''
    with resources.path(pkg, file_name) as file_path:
        # file_path 是一个 Path 对象, 输出文件的绝对路径
        config_path = str(file_path)
    if os.path.exists(config_path):
        return config_path
    logger.error(f'yml_utils.get_pkg_script {config_path} is not exits!')
    return None
 

 
if __name__ == '__main__':
    kv = get_ddb_info()
    print(kv)

