import sqlite3  # Import the SQLite3 module

__author__ = 'Chris Ottersen'

db = None
''' :type : sqlite3.Connection | None '''

cursor = None
''' :type : sqlite3.Cursor | None '''

tables = {
    "sms_type0": {
        "record_offset": "INTEGER PRIMARY KEY NOT NULL",
        "version": "TEXT",
        "u0": "BLOB",
        "message_id": "INTEGER",
        "u1": "BLOB",
        "thread_id": "INTEGER",
        "u2": "BLOB",
        "FILETIME_0": "INT8",
        "FILETIME_1": "INT8",
        "direction": "INTEGER",
        "FILETIME_2": "INT8",
        "u3": "BLOB",
        "u4": "BLOB",
        "u5": "BLOB",
        "u6": "BLOB",
        "u7": "BLOB",
        "u8": "BLOB",
        "u9": "BLOB",
        "u10": "BLOB",
        "u11": "BLOB",
        "u11a": "BLOB",
        "phone_0": "TEXT",
        "SMStext": "TEXT",
        "content": "BLOB",
        "phone_1": "TEXT",
        "phone_2": "TEXT",
        "phone_3": "TEXT",
        "message": "TEXT",
        "FILETIME_2b": "INT8",
        "u12": "BLOB",
        "FILETIME_3": "INT8",
        "sim": "TEXT",
    },

    "sms_type1": {
        "record_offset": "INTEGER PRIMARY KEY NOT NULL",
        "version": "TEXT",
        "u0": "BLOB",
        "t0": "VARCHAR(1)",
        "t1": "VARCHAR(1)",
        "t2": "VARCHAR(1)",
        "t3": "VARCHAR(1)",
        "t4": "VARCHAR(1)",
        "t5": "VARCHAR(1)",
        "i1": "VARCHAR(1)",
        "i2": "VARCHAR(1)",
        "FILETIME_0": "INT8",
        "FILETIME_1": "INT8",
        "u1": "BLOB",
        "u2": "BLOB",
        "phone_0": "TEXT",
        "SMStext": "TEXT",
        "content": "BLOB",
        "phone_1": "TEXT",
        "phone_2": "TEXT",
        "phone_3": "TEXT",
        "phone_4": "TEXT",
        "phone_5": "TEXT",
        "phone_6": "TEXT",
        "message": "TEXT",
        "FILETIME_2": "INT8",
        "u3": "BLOB",
        "u4": "BLOB",
        "u5": "BLOB",
        "u6": "BLOB",
        "u7": "BLOB",
        "u8": "BLOB",
        "FILETIME_3": "INT8",
        "FILETIME_4": "INT8",
        "FILETIME_5": "INT8",
        "FILETIME_6": "INT8",
        "FILETIME_7": "INT8",
        "message_id": "INTEGER",
        "thread_id": "INTEGER",
    },

    "sms_type2": {
        "record_offset": "INTEGER PRIMARY KEY NOT NULL",
        "version": "TEXT",
        "u0": "BLOB",
        "message_id0": "INTEGER",
        "u1": "BLOB",
        "FILETIME_0": "INT8",
        "u2": "BLOB",
        "direction": "INTEGER",
        "u3": "BLOB",
        "FILETIME_1": "INT8",
        "u4": "BLOB",
        "FILETIME_2": "INT8",
        "u5": "BLOB",
        "thread_id": "INTEGER",
        "u6": "BLOB",
        "message_id": "INTEGER",
        "u7": "BLOB",
        "phone_0": "TEXT",
        "message": "TEXT",
        "u8": "BLOB",
        "SMStext": "TEXT",
        "u9": "BLOB",
    },

    "conversation_type0": {
        "record_offset": "INTEGER PRIMARY KEY NOT NULL",
        "version": "TEXT",
        "thread_id": "INTEGER",
        "thread_length": "INTEGER",
        "u0": "BLOB",
        "FILETIME_0": "INT8",
        "u1": "BLOB",
        "phone_0": "TEXT",
        "phone_1": "TEXT",
        "phone_2": "TEXT",
        "FILETIME_1": "INT8",
        "full_binary": "BLOB"
    }
}
''' :type : dict[str, dict[str, str]] '''


def generate_tables(name, primary_key=None, columns=None, database=None, curs=None):
    """

    :param name:
    :type name: str
    :param primary_key:
    :type primary_key: str | None
    :param columns:
    :type columns: dict[str, str | None]
    :param database:
    :type database: Connection | None
    :param curs:
    :type curs: Cursor | None
    :return:
    :rtype: (Connection, Cursor)
    """
    if database is None:
        global db
        database = db
    if curs is None:
        global cursor
        curs = cursor
    if columns is None:
        global tables
        columns = tables[name]
    sub_tables = {
        "widths": {k: "INT" for k in columns.keys()},
        "offsets": {k: "INT" for k in columns.keys()},
        "stage0": {k: "BLOB" for k in columns.keys()},
        "stage1": dict(columns)
    }
    if primary_key is not None:
        sub_tables["widths"][primary_key] = columns[primary_key]
        sub_tables["offsets"][primary_key] = columns[primary_key]
        sub_tables["stage0"][primary_key] = columns[primary_key]

    curs.execute("DROP TABLE IF EXISTS %s_full_binaries;" % name)
    curs.execute(r'''
      CREATE TABLE IF NOT EXISTS
      %s_full_binaries
      (
        record_offset INTEGER PRIMARY KEY NOT NULL,
        full_binary BLOB
      );
    ''' % name)

    database.commit()
    for table in sub_tables.keys():
        curs.execute("DROP TABLE IF EXISTS %s_%s;" % (name, table))

        query = '''
            CREATE TABLE %s_%s
            (
              %s
            );
        ''' % (name,
               table,
               ",\n              ".join([("%-20s %s" % (k, sub_tables[table][k])) for k in sub_tables[table].keys()]))
        curs.execute(query)
    database.commit()

    return (database, curs)


def init_db(db_path='database/data/mydb'):
    global db
    global cursor
    try:
        # Creates or opens a file called mydb with a SQLite3 DB
        db = sqlite3.connect(db_path)
        # Get a cursor object
        cursor = db.cursor()
        generate_tables("sms_type0", "record_offset")
        generate_tables("sms_type1", "record_offset")
        generate_tables("sms_type2", "record_offset")
        generate_tables("conversation_type0", "record_offset")
        cursor.execute(r"DROP TABLE IF EXISTS dictionary;")
        cursor.execute(r'''
          CREATE TABLE
          dictionary
          (
            str TEXT PRIMARY KEY NOT NULL,
            bin_value BLOB
          );
        ''')
        db.commit()

    # Catch the exception
    except Exception as e:
        # Roll back any change if something goes wrong
        if db is not None:
            db.rollback()
        raise e
    finally:
        pass
        # Close the db connection
        # db.close()
    return db


