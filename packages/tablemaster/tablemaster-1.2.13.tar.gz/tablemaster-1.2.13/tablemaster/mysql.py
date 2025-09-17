
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from urllib.parse import quote_plus


def get_connect_args(configs):
    """
    获取数据库连接参数，支持SSL和其他通用配置
    
    Args:
        configs: 配置对象，可以包含以下属性:
            - use_ssl: 是否使用SSL (bool)
            - ssl_ca: SSL证书路径 (str)
            - connect_args: 自定义连接参数 (dict)
            - db_type: 数据库类型 ('tidb', 'mysql' 等)
    
    Returns:
        dict: 连接参数字典
    """
    connect_args = {}
    
    # 检查是否有自定义的connect_args
    if hasattr(configs, 'connect_args') and configs.connect_args:
        connect_args = configs.connect_args.copy()
    else:
        # 检查是否需要SSL
        use_ssl = getattr(configs, 'use_ssl', False)
        db_type = getattr(configs, 'db_type', 'mysql').lower()
        
        # TiDB默认使用SSL
        if db_type == 'tidb' or use_ssl:
            ssl_ca = getattr(configs, 'ssl_ca', '/etc/ssl/cert.pem')
            connect_args = {
                'ssl': {
                    'ca': ssl_ca,
                    'check_hostname': False,
                    'verify_identity': False
                }
            }
    
    return connect_args


#query function
def query(sql, configs):
    try:
        cf_port = configs.port
    except:
        cf_port = 3306
    print(f'try to connect to {configs.name}...')
    # URL-encode the password to handle special characters
    password_encoded = quote_plus(configs.password)
    
    # 获取连接参数
    connect_args = get_connect_args(configs)
    
    # 创建引擎时传入connect_args
    connection_string = f'mysql+pymysql://{configs.user}:{password_encoded}@{configs.host}:{cf_port}/{configs.database}'
    engine = create_engine(connection_string, connect_args=connect_args)
    # 直接使用engine
    conn = engine.raw_connection()
    df = pd.read_sql(sql, conn)
    
    print(df.head())
    return df

#opt function
def opt(sql, configs):
    try:
        cf_port = configs.port
    except:
        cf_port = 3306
    print(f'try to connect to {configs.name}...')
    # URL-encode the password to handle special characters
    password_encoded = quote_plus(configs.password)
    
    # 获取连接参数
    connect_args = get_connect_args(configs)
    
    # 创建引擎时传入connect_args
    engine = create_engine(
        f'mysql+pymysql://{configs.user}:{password_encoded}@{configs.host}:{cf_port}/{configs.database}',
        connect_args=connect_args,
        isolation_level="AUTOCOMMIT"
    )
    # Connect to the database using the engine's connect method
    with engine.connect() as conn:
        # Execute the SQL statement directly, without using pandas
        conn.execute(text(sql))
    print('mysql execute success!')

class ManageTable:
    def __init__(self, table, configs):
        try:
            self.port = configs.port
        except:
            self.port = 3306
        self.table = table
        self.name = configs.name
        self.user = configs.user
        self.password = quote_plus(configs.password)
        self.host = configs.host
        self.database = configs.database
        self.configs = configs  # 保存configs对象以便获取SSL等配置
        try:
            query(sql = f"SELECT * FROM {self.table} LIMIT 1", configs=configs)
            print("table exist!")
        except:
            print("table not found!")

    def delete_table(self):
        try:
            opt(f'DROP TABLE {self.table}', self.configs)
            print(f'{self.table} deleted!')
        except:
            print('Table was not deleted!')

    def par_del(self, clause):
        del_clause = f"DELETE FROM {self.table} WHERE {clause}"
        opt(del_clause, self.configs)
        print(f'records of table that {clause} are deleted!')

    def change_data_type(self, cols_name, data_type):
        change_clause = f'ALTER TABLE {self.table} MODIFY COLUMN {cols_name} {data_type}'
        opt(change_clause, self.configs)
        print(f'{cols_name} changed to {data_type} successfully!')


    def upload_data(self, df, chunk_size=10000, add_date=False):
        # 获取连接参数
        connect_args = get_connect_args(self.configs) if hasattr(self, 'configs') else get_connect_args(self)
        
        db_url = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
        engine = create_engine(db_url, connect_args=connect_args)
        
        with engine.begin() as connection:
            # Add a 'rundate' column with the current date formatted as 'YYYY-MM-DD' if required
            if add_date:
                df_copy = df.copy()
                df_copy['rundate'] = datetime.now().strftime('%Y-%m-%d')
            else:
                df_copy = df
            total_chunks = (len(df_copy) // chunk_size) + (0 if len(df_copy) % chunk_size == 0 else 1)
            print(f'try to upload data now, chunk_size is {chunk_size}')
            with tqdm(total=total_chunks, desc="Uploading Chunks", unit="chunk") as pbar:
                try:
                    for start in range(0, len(df_copy), chunk_size):
                        end = min(start + chunk_size, len(df_copy))
                        chunk = df_copy.iloc[start:end]
                        chunk.to_sql(name=self.table, con=connection, if_exists='append', index=False)
                        pbar.update(1)
                except Exception as e:
                    print(f"An error occurred: {e}")

    def upsert_data(self, df, chunk_size=10000, add_date=False, ignore=False):
        # 获取连接参数
        connect_args = get_connect_args(self.configs) if hasattr(self, 'configs') else get_connect_args(self)
        
        db_url = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
        engine = create_engine(db_url, connect_args=connect_args)

        with engine.begin() as connection:
            # Add a 'rundate' column with the current date formatted as 'YYYY-MM-DD' if required
            if add_date:
                df_copy = df.copy()
                df_copy['rundate'] = datetime.now().strftime('%Y-%m-%d')
            else:
                df_copy = df

            total_chunks = (len(df_copy) // chunk_size) + (0 if len(df_copy) % chunk_size == 0 else 1)
            print(f'Trying to upload data now, chunk_size is {chunk_size}')

            with tqdm(total=total_chunks, desc="Uploading Chunks", unit="chunk") as pbar:
                for start in range(0, len(df_copy), chunk_size):
                    end = min(start + chunk_size, len(df_copy))
                    chunk = df_copy.iloc[start:end]
                    columns = chunk.columns.tolist()
                    update_columns = ', '.join([f"`{col}`=VALUES(`{col}`)" for col in columns])

                    try:
                        if ignore == False:
                            # Use INSERT ... ON DUPLICATE KEY UPDATE (Use the new value to replace old value)
                            insert_sql = f"""
                            INSERT INTO {self.table} ({', '.join([f'`{col}`' for col in columns])})
                            VALUES ({', '.join(['%s'] * len(columns))})
                            ON DUPLICATE KEY UPDATE {update_columns}
                            """
                        else:
                            # Ignore the duplicate key rows (Keep the old value)
                            insert_sql = f"""
                            INSERT IGNORE INTO {self.table} ({', '.join([f'`{col}`' for col in columns])})
                            VALUES ({', '.join(['%s'] * len(columns))})
                            """

                        data = [tuple(row) for row in chunk.to_numpy()]
                        with connection.connection.cursor() as cursor:
                            cursor.executemany(insert_sql, data)
                        connection.connection.commit()
                        pbar.update(1)
                    except Exception as e:
                        print(f"An error occurred: {e}")

# Old ManageTable Way
class Manage_table:
    def __init__(self, table, configs):
        print('We recommend using ManageTable for MySQL table management instead of Manage_table. e.g. tb=ManageTable(...)')
        try:
            self.port = configs.port
        except:
            self.port = 3306
        self.table = table
        self.name = configs.name
        self.user = configs.user
        self.password = configs.password
        self.host = configs.host
        self.database = configs.database
        self.configs = configs  # 保存configs对象以便获取SSL等配置
        try:
            query(sql = f"SELECT * FROM {self.table} LIMIT 1", configs=configs)
            print("table exist!")
        except:
            print("table not found!")

    def delete_table(self):
        opt(f'DROP TABLE {self.table}', self.configs)
        print(f'{self.table} deleted!')

    def par_del(self, clause):
        del_clause = f"DELETE FROM {self.table} WHERE {clause}"
        opt(del_clause, self)
        print(f'records of table that {clause} are deleted!')

    def change_data_type(self, cols_name, data_type):
        change_clause = f'ALTER TABLE {self.table} MODIFY COLUMN {cols_name} {data_type}'
        opt(change_clause, self.configs)
        print(f'{cols_name} changed to {data_type} successfully!')


    def upload_data(self, df, chunk_size=10000, add_date=True):
        # 获取连接参数
        connect_args = get_connect_args(self.configs) if hasattr(self, 'configs') else get_connect_args(self)
        
        # URL-encode the password
        password_encoded = quote_plus(self.password)
        db_url = f'mysql+pymysql://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.database}'
        engine = create_engine(db_url, connect_args=connect_args)
        
        with engine.begin() as connection:
            # Add a 'rundate' column with the current date formatted as 'YYYY-MM-DD' if required
            if add_date:
                df_copy = df.copy()
                df_copy['rundate'] = datetime.now().strftime('%Y-%m-%d')
            else:
                df_copy = df
            total_chunks = (len(df_copy) // chunk_size) + (0 if len(df_copy) % chunk_size == 0 else 1)
            print(f'try to upload data now, chunk_size is {chunk_size}')
            with tqdm(total=total_chunks, desc="Uploading Chunks", unit="chunk") as pbar:
                try:
                    for start in range(0, len(df_copy), chunk_size):
                        end = min(start + chunk_size, len(df_copy))
                        chunk = df_copy.iloc[start:end]
                        chunk.to_sql(name=self.table, con=connection, if_exists='append', index=False)
                        pbar.update(1)
                except Exception as e:
                    print(f"An error occurred: {e}")
