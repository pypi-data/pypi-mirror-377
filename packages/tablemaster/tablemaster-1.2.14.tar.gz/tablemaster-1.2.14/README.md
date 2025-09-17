# tablemaster
A Python package makes it easy to manage tables anywhere.

# Install
```
pip install -U tablemaster
```

# Preparation
### To use the function related to mysql, need to put a file named cfg.yaml in the same path, which is like:
```
 db_name_example:
   name: db_name_example
   user: user_name_example
   password: pw_example
   host: host_example
   database: db_example
```

### To use the function related to google sheet, here is the guide:
https://docs.gspread.org/en/latest/oauth2.html

# Examples of Mysql Part

## query from mysql
```
import tablemaster as tm

sql_query = 'SELECT * FROM table_name LIMIT 20'
df = tm.query(sql_query, tm.cfg.db_name)
df
```

## change column name
```
import tablemaster as tm

sql_query = ('ALTER TABLE table_name RENAME COLUMN column1 TO column2')
tm.opt(sql_query, tm.cfg.db_name)
```

## create a table in mysql and upload data from dataframe df
```
import tablemaster as tm

tb = tm.ManageTable('table_name_2', tm.cfg.db1)
tb.upload_data(df, add_date=True)
```

## delete a table in mysql
```
import tablemaster as tm

tb = tm.ManageTable('table_name_2', tm.cfg.db1)
tb.delete_table()
```

## delete rows in mysql with condition
```
import tablemaster as tm

tb = tm.ManageTable('table_name_2', tm.cfg.db1)
tb.par_del("order_date > '2023-01-01' ")
```

## change data type of the mysql table
```
import tablemaster as tm

tb = tm.ManageTable('table_name_2', tm.cfg.db1)
tb.change_data_type('col_a', 'VARCHAR(10)')
```

# Examples of Google Sheet Part
## read table from google sheet
```
import tablemaster as tm

google_sheet = ('GoogleSheet Table Name', 'GoogleSheet Sheet Name')
df = tm.gs_read_df(google_sheet)
df
```

## write data df to google sheet
```
import tablemaster as tm

google_sheet = ('GoogleSheet Table Name', 'GoogleSheet Sheet Name')
tm.gs_write_df(google_sheet, df)
```
# Examples of Feishu/Lark Part
## read table from feishu(lark)
```
import tablemaster as tm

feishu_sheet = ('Feishu Sheet ID Name', 'Feishu Sheet Table Name')
df = tm.fs_read_df(feishu_sheet)
df
```

## read base from feishu(lark)
```
import tablemaster as tm

feishu_base = ('Feishu Base ID Name', 'Feishu Base Table Name')
df = tm.fs_read_base(feishu_base)
df
```
# Examples of Local Part
## import one file from local
```
import tablemaster as tm

df = tm.read("*Part of File Name*")
df
```

## batch import and merge
```
import tablemaster as tm

df = tm.batch_read("*Part of File Name*")
df
```

## batch import without merging
```
import tablemaster as tm

df = tm.read_dfs("*Part of File Name*")
df
```
