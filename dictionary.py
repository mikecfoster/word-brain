import sqlite3

def create_sqlite_database(db):
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db)
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_tables(db):
    sql_drop_table = """
        DROP TABLE IF EXISTS words;
    """
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS words ( word TEXT );
        """

    # create a database connection
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_drop_table)
            cursor.execute(sql_create_table)
            conn.commit()
            print("table 'words' created")
    except sqlite3.Error as e:
        print(e)


def load_words(db, filename):
    # create a database connection
    print("Adding words to the dictionary")
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
                
            with open(filename) as word_file:
                for word in word_file.read().split():
                    sql = ''' INSERT INTO words VALUES (?) '''
                    cursor.execute(sql, (word,))
                conn.commit()  

    except sqlite3.Error as e:
        print(e)


if __name__ == '__main__':
    # english_words = load_words()
    # demo print
    # print('fate' in english_words)
    db = "dict.db"
    create_sqlite_database(db)
    create_tables(db)
    load_words(db, 'words_alpha.txt')


