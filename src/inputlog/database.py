import os
import time
import sqlite3
import platform
import tkinter


'''
0-----------------------------------------------------------------------------0
| SQL SETTINGS                                                                |
0-----------------------------------------------------------------------------0
'''

class SQL_KEY:
    # Mouse identifiers
    mouse = 'm'
    pos = 'p'
    click = 'c'
    scroll = 's'
    # Keyboard identifiers
    key = 'k'
    up = 'u'
    down = 'd'
    char = 'c'
    other = 'o'
    none = 'n'


'''
0-----------------------------------------------------------------------------0
| SQL SETTINGS                                                                |
0-----------------------------------------------------------------------------0
'''

def create_database(database: str):
    database = str(database)
    connection = None

    # Check input
    if not database.endswith('.db'):
        raise TypeError('Database must be in ".db" format!')
    if os.path.isfile(database):
        raise FileExistsError('Database already exists!')

    try:
        # Open database connection
        connection = sqlite3.connect(database, check_same_thread=False)

        # Create metadata table
        connection.execute("CREATE TABLE metadata (key TEXT NOT NULL, value TEXT NOT NULL);")
        connection.execute(f"""
            INSERT INTO metadata (key, value) VALUES 
            ('user', '{os.getlogin()}'),
            ('node', '{platform.node()}'),
            ('system', '{platform.system()}'),
            ('version', '{platform.version()}'),
            ('start_time', '{int(time.time() * 1000)}'),
            ('screen_width', '{tkinter.Tk().winfo_screenwidth()}'),
            ('screen_height', '{tkinter.Tk().winfo_screenheight()}');
        """)
        # Create key_ids table
        connection.execute("CREATE TABLE key_ids (key TEXT NOT NULL, value TEXT NOT NULL);")
        connection.execute(f"""
            INSERT INTO key_ids (key, value) VALUES 
            ('{SQL_KEY.mouse}', 'mouse'),
            ('{SQL_KEY.pos}', 'pos'),
            ('{SQL_KEY.click}', 'click'),
            ('{SQL_KEY.scroll}', 'scroll'),
            ('{SQL_KEY.key}', 'key'),
            ('{SQL_KEY.up}', 'up'),
            ('{SQL_KEY.down}', 'down'),
            ('{SQL_KEY.char}', 'char'),
            ('{SQL_KEY.other}', 'other'),
            ('{SQL_KEY.none}', 'none');
        """)
        # Create (primary) events table
        connection.execute(f"""
            CREATE TABLE events (
                id        INTEGER PRIMARY KEY, 
                device    TEXT NOT NULL CHECK(device IN ('{SQL_KEY.mouse}', '{SQL_KEY.key}')),
                event     TEXT NOT NULL CHECK(event IN ('{SQL_KEY.pos}', '{SQL_KEY.click}', '{SQL_KEY.scroll}', '{SQL_KEY.down}', '{SQL_KEY.up}')),
                timestamp INTEGER NOT NULL
             );
        """)
        connection.execute("""
            CREATE TABLE mouse_pos_events (
                event_id INTEGER PRIMARY KEY, 
                x        INTEGER NOT NULL,
                y        INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE);
        """)
        connection.execute(f"""
            CREATE TABLE mouse_click_events (
                event_id INTEGER PRIMARY KEY, 
                x        INTEGER NOT NULL,
                y        INTEGER NOT NULL,
                button   TEXT NOT NULL,
                pressed  TEXT NOT NULL CHECK(pressed IN ('{SQL_KEY.up}', '{SQL_KEY.down}')),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE);
        """)
        connection.execute("""
            CREATE TABLE mouse_scroll_events (
                event_id INTEGER PRIMARY KEY, 
                x        INTEGER NOT NULL,
                y        INTEGER NOT NULL,
                scroll   INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE);
        """)
        connection.execute(f"""
            CREATE TABLE keyboard_events (
                event_id INTEGER PRIMARY KEY, 
                key      TEXT NOT NULL,
                type     TEXT NOT NULL CHECK(type IN ('{SQL_KEY.char}', '{SQL_KEY.other}', '{SQL_KEY.none}')),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE);
        """)
        # Commit results
        connection.commit()
        return connection

    except sqlite3.Error as error:
        # Close connection
        if connection is not None:
            connection.close()
        # Delete the database
        os.remove(database)
        raise ConnectionError('Database creation error: ', error)
