import os
import yaml
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import ResourceClosedError
from urllib.parse import quote_plus


def get_connect_args(cfg: dict) -> dict:
    """
    获取数据库连接参数，支持SSL和其他通用配置
    
    Args:
        cfg: 配置字典，可以包含以下键:
            - use_ssl: 是否使用SSL (bool)
            - ssl_ca: SSL证书路径 (str)
            - connect_args: 自定义连接参数 (dict)
            - db_type: 数据库类型 ('tidb', 'mysql' 等)
    
    Returns:
        dict: 连接参数字典
    """
    connect_args = {}
    
    # 检查是否有自定义的connect_args
    if 'connect_args' in cfg and cfg['connect_args']:
        connect_args = cfg['connect_args'].copy()
    else:
        # 检查是否需要SSL
        use_ssl = cfg.get('use_ssl', False)
        db_type = cfg.get('db_type', 'mysql').lower()
        
        # TiDB默认使用SSL
        if db_type == 'tidb' or use_ssl:
            ssl_ca = cfg.get('ssl_ca', '/etc/ssl/cert.pem')
            connect_args = {
                'ssl': {
                    'ca': ssl_ca,
                    'check_hostname': False,
                    'verify_identity': False
                }
            }
    
    return connect_args


def load_db_config(yaml_file_name: str, database: str, custom_path: Optional[str] = None) -> dict:
    """加载数据库配置"""
    file_path = os.path.join(custom_path, yaml_file_name) if custom_path else yaml_file_name
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config.get(database, {})

def connect_to_db(cfg: dict):
    """创建数据库连接，支持SSL配置"""
    try:
        # URL-encode the password to handle special characters
        password_encoded = quote_plus(cfg['password'])
        
        # 获取连接参数
        connect_args = get_connect_args(cfg)
        
        # 创建连接字符串
        connection_string = f"mysql+pymysql://{cfg['user']}:{password_encoded}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        
        # 创建引擎时传入connect_args
        engine = create_engine(connection_string, connect_args=connect_args)
        return engine
    except KeyError as e:
        raise ValueError(f"配置中缺少必要的键：{e}")

def clean_dataframe(df: pd.DataFrame):
    """清理DataFrame中的无穷值"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        inf_values = df[numeric_cols].isin([np.inf, -np.inf]).any()
        cols_with_inf = inf_values[inf_values].index.tolist()
        if cols_with_inf:
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            print(f"警告：以下列包含无穷值，已替换为NaN：{cols_with_inf}")

def execute_sql(engine, sql_statement: str):
    """执行SQL语句"""
    try:
        with engine.begin() as conn:
            conn.execute(text(sql_statement))
    except Exception as e:
        raise ValueError(f"执行SQL时发生错误：{e}")

def update(
        raw_df: pd.DataFrame,
        database: str,
        table: str,
        yaml_file_name: str = 'cfg.yaml',
        clause: Optional[str] = None,
        date_col: Optional[str] = None,
        custom_path: Optional[str] = None
    ):
    try:
        df = raw_df.copy()
        if df.empty:
            raise ValueError("导入的数据集为空。")
        
        # 清理数据
        clean_dataframe(df)
        
        # 加载数据库配置
        cfg = load_db_config(yaml_file_name, database, custom_path)
        
        # 连接数据库
        engine = connect_to_db(cfg)
        
        # 测试写入一行数据
        test_df = df.iloc[[0]].copy()
        try:
            test_df.to_sql(table, engine, if_exists='append', index=False)
        except Exception as e:
            raise ValueError(f"测试写入数据失败，请检查数据格式：{str(e)}")
        
        # 如果指定了日期列，添加日期条件
        if date_col and date_col in df.columns:
            min_date = df[date_col].min()
            max_date = df[date_col].max()
            print(f"更新的数据日期范围：{min_date} ~ {max_date}")
            if clause:
                clause = f"{clause} AND {date_col} >= '{min_date}' AND {date_col} <= '{max_date}'"
            else:
                clause = f"{date_col} >= '{min_date}' AND {date_col} <= '{max_date}'"
        
        # 如果有条件子句，先删除符合条件的数据
        if clause:
            delete_sql = f"DELETE FROM {table} WHERE {clause}"
            execute_sql(engine, delete_sql)
        
        # 将数据写入数据库
        df.to_sql(table, engine, if_exists='append', index=False)
        
        print(f"成功更新 {len(df)} 条记录到 {database}.{table}")
        
    except Exception as e:
        raise Exception(f"更新数据时发生错误：{str(e)}")


def print_action_result(table: str, action: str, df: pd.DataFrame, df_date_col: Optional[str] = None):
    """打印操作结果"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    if df_date_col:
        date_range = f"{df[df_date_col].min()} 至 {df[df_date_col].max()}"
        print(f"{table} 数据已{action}：{current_time}\n数据日期范围：{date_range}")
    else:
        print(f"{table} 数据已{action}：{current_time}")

def sql_query(
        database: str,
        sql: str,
        yaml_file_name: str='cfg.yaml',
        custom_path: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
    """执行SQL查询"""
    cfg = load_db_config(yaml_file_name, database, custom_path)
    engine = connect_to_db(cfg)
    try:
        if sql.strip().upper().startswith("SELECT"):
            df = pd.read_sql(sql, engine)
            return df
        else:
            execute_sql(engine, sql)
            print('操作完成。')
    except ResourceClosedError:
        print('查询完成，但没有返回任何数据。')
    except Exception as e:
        raise ValueError(f"执行SQL查询时发生错误：{e}")
