import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("DB created")
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try: 
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

# Insert Data to Distance Table
def create_distance_record(conn, user_record):
    sql_query = """INSERT INTO distance_record (username, distance, game_id)
                   VALUES(?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql_query, user_record)
    conn.commit()
    return cur.lastrowid

# Insert Data to LeaderBoard Table
def create_game_record(conn, game_record):
    game_record.append(datetime.utcnow().strftime("%d-%m-%y"))
    sql_query = """INSERT into position_history(first, second, third, fourth, fifth, sixth, date) 
                   VALUES(?,?,?,?,?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql_query, game_record) 
    conn.commit()
    return cur.lastrowid

# Get Highscores
def select_highscore(conn):
    sql_query = """SELECT username, distance FROM distance_record ORDER BY distance LIMIT 5"""
    cur = conn.cursor()
    cur.execute(sql_query)
    return cur.fetchall()

# Get Today's Game Records
def select_game_records(conn, source, date):
    sql_query = """SELECT * FROM position_history WHERE date=?"""
    cur = conn.cursor()
    cur.execute(sql_query, date)
    return cur.fetchall()



if __name__ == "__main__":
    database = "db/racegame.db"
    sql_create_position_history_table = """ CREATE TABLE IF NOT EXISTS position_history (
                                            id integer PRIMARY KEY,
                                            first text NOT NULL,
                                            second text,
                                            third text,
                                            fourth text,
                                            fifth text,
                                            sixth text,
                                            date text NOT NULL
                                         ); """

    sql_create_distance_record_table = """CREATE TABLE IF NOT EXISTS distance_record (
                                          id integer PRIMARY KEY,
                                          username text NOT NULL,
                                          distance integer NOT NULL,
                                          game_id integer NOT NULL,
                                          FOREIGN KEY (game_id) REFERENCES position_history (id)
                                      );"""
    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_position_history_table)

        create_table(conn,sql_create_distance_record_table)
    else:
        print("Error! Cannot create connection")
        
