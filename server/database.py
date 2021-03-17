import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try: 
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_news(conn, article, source):
    article.append(datetime.utcnow().strftime("%d-%m-%y"))
    article.append(source)
    sql_query = """INSERT INTO news(headline,link,og_compound_rating,og_negative_rating, og_neutral_rating, og_positive_rating, date, source)
                   VALUES(?,?,?,?,?,?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql_query, article)
    conn.commit()
    return cur.lastrowid

def select_news_by_source(conn, source):
    sql_query = """SELECT * FROM news WHERE source=?"""
    cur = conn.cursor()
    cur.execute(sql_query, (source,))
    return cur.fetchall()

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
    database = "db/news.db"
    sql_create_news_table = """ CREATE TABLE IF NOT EXISTS news (
                                        id integer PRIMARY KEY,
                                        headline text NOT NULL,
                                        link text NOT NULL,
                                        source text NOT NULL,
                                        og_compound_rating real NOT NULL,
                                        og_negative_rating real NOT NULL,
                                        og_neutral_rating real NOT NULL,
                                        og_positive_rating real NOT NULL,
                                        date text NOT NULL
                                    ); """

    sql_create_votes_table = """CREATE TABLE IF NOT EXISTS votes (
                                    id integer PRIMARY KEY,
                                    vote text NOT NULL,
                                    news_id integer NOT NULL,
                                    last_updated text NOT NULL,
                                    FOREIGN KEY (news_id) REFERENCES news (id)
                                );"""
    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_news_table)

        create_table(conn,sql_create_votes_table)
    else:
        print("Error! Cannot create connection")
        
    print(select_news_by_source(conn, "mothership"))
    vote_news(conn, 1, 'postive' )