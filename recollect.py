import sqlite3
global db
global sql
db=sqlite3.connect('server.db', check_same_thread=False)
sql=db.cursor()
db.commit()
global true_db
global true_sql
true_db=sqlite3.connect('alldates.db', check_same_thread=False)
true_sql=true_db.cursor()
true_sql.execute("""CREATE TABLE IF NOT EXISTS dates (info TEXT, day TEXT, month TEXT, year TEXT, fulldate TEXT)""")
true_db.commit()


sql.execute("SELECT * FROM dates")
results=sql.fetchall()
for result in results:
    info=result[0]
    day=result[1][0:2]
    month=result[1][3:5]
    year=result[1][6:]
    fullyear=result[1]
    true_sql.execute("INSERT INTO dates VALUES (?, ?, ?, ?, ?)", (info, day, month, year, fullyear))
    true_db.commit()
    print(f"----------\n{info}\n{day}.{month}.{year} ({fullyear})")