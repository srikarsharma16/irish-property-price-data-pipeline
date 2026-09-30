import re, sys, sqlite3, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", 60); pd.set_option("display.max_rows", 200)
arg = sys.argv[1]
sql = open(arg, encoding="utf-8").read() if arg.endswith(".sql") else arg
con = sqlite3.connect("data/finance.db")
for stmt in [s.strip() for s in sql.split(";") if re.search(r"\b(select|with)\b", s, re.I)]:
    print(pd.read_sql_query(stmt, con).to_string(index=False)); print()
