import sqlite3

DB = "movies.db"

schema = [
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)",
    "CREATE TABLE IF NOT EXISTS preferences (user_id INTEGER PRIMARY KEY, genres TEXT, FOREIGN KEY(user_id) REFERENCES users(id))",
    "CREATE TABLE IF NOT EXISTS ratings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, movie_id INTEGER, rating INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))",
]


def init_db(path=DB):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    for s in schema:
        cur.execute(s)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Initialized database:\n - users\n - preferences\n - ratings")
