import sqlite3

def get_conn(db="College.db"):
    conn = sqlite3.connect(db)
    print("DB connected")
    return conn

def create_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS students(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, age INTEGER, grade TEXT)''')
    conn.commit()
    print("Tbl created.")

def drop_table(conn):
    conn.execute('DROP TABLE IF EXISTS students')
    conn.commit()
    print("Tbl droped.")

def insert(conn, n, a, g):
    conn.execute('INSERT INTO students(name,age,grade) VALUES(?,?,?)', (n,a,g))
    conn.commit()
    print(f"{n} added, age {a}, grade {g}")

def update(conn, sid, g):
    conn.execute('UPDATE students SET grade=? WHERE id=?', (g,sid))
    conn.commit()
    print(f"ID {sid} update to {g}")

def show_all(conn):
    rows = conn.execute('SELECT * FROM students').fetchall()
    print("\nAll stdnts:" if rows else "\n(No recs)")
    for r in rows: print(r)

conn = get_conn()
create_table(conn)

while True:
    ch = input("\n1.Add 2.Update 3.Show 4.Drop 5.Exit: ").strip()
    if ch=="1":
        n=input("Name: "); a=int(input("Age: ")); g=input("Grade: ")
        insert(conn,n,a,g)
    elif ch=="2":
        sid=int(input("ID to upd: ")); g=input("New grd: ")
        update(conn,sid,g)
    elif ch=="3": show_all(conn)
    elif ch=="4":
        if input("Drop tbl (y/n): ").lower()=="y": drop_table(conn)
    elif ch=="5": break
    else: print("Invld choice")

conn.close()
print("DB closed")
