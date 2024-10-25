import sys
import os.path as osp
from typing import List, Dict, Tuple
import psycopg2 as pg
from sshtunnel import SSHTunnelForwarder
import pandas as pd

current_path = osp.dirname(osp.realpath(__file__))
sys.path.append(current_path)
import utils as cutils


def load_db_config(filename="YOUR OWN DB CONFIG PATH"):
    return cutils.load_yaml(filename)


def connect_ppg2(db_config):
    ssh_tunnel = None
    try:
        if "SSHTunnel" in db_config:
            ssh_tunnel = SSHTunnelForwarder(
                (db_config["SSHTunnel"]["host"], db_config["SSHTunnel"]["port"]),
                ssh_username=db_config["SSHTunnel"]["user"],
                ssh_password=db_config["SSHTunnel"]["passwd"],
                remote_bind_address=(
                    db_config["Database"]["host"],
                    db_config["Database"]["port"],
                ),
            )
            ssh_tunnel.start()

            conn = pg.connect(
                host="localhost",
                user=db_config["Database"]["user"],
                password=db_config["Database"]["passwd"],
                port=ssh_tunnel.local_bind_port,
                database=db_config["Database"]["dbname"],
            )
        else:
            conn = pg.connect(
                host=db_config["Database"]["host"],
                user=db_config["Database"]["user"],
                password=db_config["Database"]["passwd"],
                port=db_config["Database"]["port"],
                database=db_config["Database"]["dbname"],
            )
        return conn
    except:
        print("Connection Has Failed...")
        if ssh_tunnel:
            ssh_tunnel.close()


def execute_sql_ppg2(query, db_config) -> List:
    db_cursor = connect_ppg2(db_config).cursor()
    db_cursor.execute(query)
    records = db_cursor.fetchall()
    return records


def create_df_from_ppg2(query, db_config) -> pd.DataFrame:
    conn = connect_ppg2(db_config)
    return pd.read_sql_query(query, conn)


def create_table_ppg2(df, conn, table_name, schema_name):
    df.to_sql(
        con=conn, name=table_name, schema=schema_name, if_exists="replace", index=False
    )


if __name__ == "__main__":
    db_config = load_db_config(
        f"{current_path}/../config/YOUR OWN DB CONFIG PATH"
    )
    query = f"select * from {db_config['Database']['schema']}.numeric_data limit 10"
    res = execute_sql_ppg2(query, db_config)
    df = create_df_from_ppg2(query, db_config)
