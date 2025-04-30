import sqlite3
import numpy as np

from inputlog.database import SQL_KEY


# Define main function
def main():
    connection = None

    # Main logic
    try:

        # Connect to a database
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()

        # # SQL debugger
        # def debug(sql_query: str):
        #     cursor.execute(sql_query)
        #     output = cursor.fetchall()
        #     for row in output:
        #         print(row)

        # Query key presses
        cursor.execute(f"""
            SELECT key FROM events 
            JOIN keyboard_events 
                ON events.id = keyboard_events.event_id 
            WHERE event = '{SQL_KEY.down}' and type = '{SQL_KEY.type_alphanum}';
        """)
        alphanum_keys = np.asarray(cursor.fetchall())

        # Combine key presses
        text = ''
        for key in alphanum_keys:
            text = text + key

        # Show results
        print(text)


    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)

    # Close connection
    finally:
        if connection:
            connection.close()
            print('SQLite Connection closed')


# Run main function
if __name__ == '__main__':
    main()
