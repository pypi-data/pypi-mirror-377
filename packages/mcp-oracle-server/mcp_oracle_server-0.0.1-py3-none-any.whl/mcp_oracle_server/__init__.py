import os
import sys
import signal
from typing import Any
from mcp.server.fastmcp import FastMCP
from . import oracle_tools
from dotenv import load_dotenv
import oracledb

# Load the environment variables
load_dotenv()

# Initialize the FastMCP server
mcp = FastMCP("mcp-oracle-server")

@mcp.tool(description=r"获取oracle数据库中的所有表名或者指定schema下的所有表名。 注意：owner参数可以不指定，如果不指定，则会查询所有schema下的表，但如果表数量超过100张，则只会返回前100张")
async def list_tables(owner: str="") -> str:
    """"获取oracle数据库中的所有表名或者指定schema下的所有表名。 注意：owner参数可以不指定，如果不指定，则会查询所有schema下的表，但如果表数量超过100张，则只会返回前100张"
    Args:
        owner：(string, optional): The owner/schema of the tables to list. Defaults to "".
    """
    return await oracle_tools.list_tables(owner)


@mcp.tool(description=r"获取oracle数据库中指定表的描述信息，比如字段名，字段类型等。 "
                      r"注意：入参table_name和owner，其中table_name为表名，owner可以不指定，如果不指定，则会查询所有schema下的表")
async def describe_table(table_name: str, owner: str="") -> str:
    """获取oracle数据库中指定表的描述信息，比如字段名，字段类型等。
        注意：入参table_name和owner，其中table_name为表名，owner可以不指定，如果不指定，则会查询所有schema下的表
    Args:
        table_name (string): The name of the table to describe
        owner (string, optional): The owner/schema of the table. Defaults to "".
    """
    return await oracle_tools.describe_table(table_name, owner)


@mcp.tool(description="执行oracle查询操作。注意：入参为 sql 查询语句，需要指定表的owner，比如 select * from urp3.testtable。")
async def read_query(query: str) -> str:
    """执行oracle查询操作。注意：入参为 sql 查询语句，需要指定表的owner，比如 select * from urp3.testtable。
    Args:
        query (string): The sql query to execute
    """
    return await oracle_tools.read_query(query)


@mcp.tool(description="执行oracle插入、更新、删除等操作。使用前必须和用户确认。 注意：入参为 sql DML 语句，需要指定表的owner，比如 update urp3.testtable set name='newname' where id=1")
async def exec_dml_sql(execsql: str) -> str:
    """执行oracle插入、更新、删除等操作。使用前必须和用户确认。 注意：入参为 sql DML 语句，需要指定表的owner，比如 update urp3.testtable set name='newname' where id=1
    Args:
        execsql (string): The sql DML statement to execute
    """
    return await oracle_tools.exec_dml_sql(execsql)

@mcp.tool(description="执行oracle创建、删除、修改表等DDL操作。 使用前必须和用户确认。注意：入参为 sql DDL 语句，需要指定表的owner，比如 create table urp3.newtable (id number, name varchar2(50))")
async def exec_ddl_sql(execsql: str) -> str:
    """执行oracle创建、删除、修改表等DDL操作。 使用前必须和用户确认。注意：入参为 sql DDL 语句，需要指定表的owner，比如 create table urp3.newtable (id number, name varchar2(50))

    Args:
        execsql (string): The sql DDL statement to execute
    """
    return await oracle_tools.exec_ddl_sql(execsql)

@mcp.tool(description="执行oracle的PL/SQL代码块，包括存储过程、函数和匿名块。 使用前必须和用户确认。注意：入参为 PL/SQL 代码块，比如 begin my_procedure(param1, param2); end;")
async def exec_pro_sql(execsql: str) -> str:
    """执行oracle的PL/SQL代码块，包括存储过程、函数和匿名块。 使用前必须和用户确认。注意：入参为 PL/SQL 代码块，比如 begin my_procedure(param1, param2); end;

    Args:
        execsql (string): The PL/SQL code block to execute
    """
    return await oracle_tools.exec_pro_sql(execsql)


def main() -> None:
    mcp.run(transport='stdio')
    # mcp.run(transport='http', host='0.0.0.0', port=8080)

def main_http() -> None:
    mcp.run(transport="sse")


def dev() -> None:
    """
    Development function that handles Ctrl+C gracefully.
    This function calls main() but catches KeyboardInterrupt to allow 
    clean exit when user presses Ctrl+C.
    """
    print("mcp server starting", file=sys.stderr)

    # Define signal handler for cleaner exit
    def signal_handler(sig, frame):
        print("\nShutting down mcp server...", file=sys.stderr)
        sys.exit(0)

    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Run the server with proper exception handling
        main()
    except KeyboardInterrupt:
        print("\nShutting down mcp server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
