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

def create_distance_record(conn, article, source):
    article.append(datetime.utcnow().strftime("%d-%m-%y"))
    article.append(source)
    sql_query = """INSERT INTO news(headline,link,og_compound_rating,og_negative_rating, og_neutral_rating, og_positive_rating, date, source)
                   VALUES(?,?,?,?,?,?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql_query, article)
    conn.commit()
    return cur.lastrowid

def select_news_by_source_date(conn, source, date):
    sql_query = """SELECT * FROM news WHERE source=? and date=?"""
    cur = conn.cursor()
    cur.execute(sql_query, (source, date, ))
    return cur.fetchall()


def select_vote_by_news_id(conn, news_id):
    sql_query = """SELECT * FROM votes WHERE news_id=?"""
    cur = conn.cursor()
    cur.execute(sql_query, (news_id,))
    return cur.fetchall()


def vote_news(conn, news_id, vote):
    last_updated = datetime.utcnow().strftime("%d/%m/%y")
    sql_query = """INSERT into votes(vote,news_id,last_updated) 
                   VALUES(?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql_query, (vote,news_id, last_updated))
    conn.commit()
    return cur.lastrowid

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

    sql_create_distance_record_table = """CREATE TABLE IF NOT EXISTS votes (
                                          id integer PRIMARY KEY,
                                          username text NOT NULL,
                                          distance integer NOT NULL,
                                          game_id integer NOT NULL,
                                          last_updated text NOT NULL,
                                          FOREIGN KEY (game_id) REFERENCES position_history (id)
                                      );"""
    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_position_history_table)

        create_table(conn,sql_create_distance_record_table)
    else:
        print("Error! Cannot create connection")
        
