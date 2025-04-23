import os
import sys
import sqlite3
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# Define main function
def main():
    connection = None
    # Main logic
    try:

        # Connect to a database
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()

        # SQL debugger
        def debug(sql_query: str):
            cursor.execute(sql_query)
            output = cursor.fetchall()
            for row in output:
                print(row)

        # DEBUG
        debug("""
        SELECT * FROM 
        
        
        """)



        # Get metadata
        cursor.execute("SELECT * FROM metadata;")
        metadata = dict(cursor.fetchall())

        # Get screen information
        screen_size = np.asarray([int(metadata['screen_width']), int(metadata['screen_height'])])

        # Query the mouse position
        cursor.execute("""
            SELECT x, y FROM events 
            JOIN mouse_pos_events 
                ON events.id = mouse_pos_events.event_id;
        """)
        mouse_pos = np.asarray(cursor.fetchall())

        # Query the mouse position
        cursor.execute("""
            SELECT x, y FROM events 
            JOIN mouse_click_events 
                ON events.id = mouse_click_events.event_id 
            WHERE pressed = 'd';
        """)
        mouse_click = cursor.fetchall()
        mouse_click = np.asarray(mouse_click)

        # Create screen image
        screen_scale = 0.5
        screen_size_scaled = (screen_scale * screen_size).astype('int')
        screen_image_scaled = np.zeros(shape=screen_size_scaled[::-1], dtype='uint')


        # Create a figure
        aspect = screen_size[1] / screen_size[0]
        fig, ax = plt.subplots(figsize=(10, 10 * aspect))

        # Show the image
        extent = (0.0, float(screen_size[0]), float(screen_size[1]), 0.0)
        plt.imshow(screen_image_scaled, cmap='binary', extent=extent, interpolation=None)

        # Plot mouse movement
        plt.plot(mouse_pos[:, 0], mouse_pos[:, 1], '-b', label='Mouse pos')

        # Plot mouse clicks
        plt.plot(mouse_click[:, 0], mouse_click[:, 1], 'or', label='Mouse click')

        # Settings
        plt.title(f'Screen size - {screen_size[0]} x {screen_size[1]}')
        plt.tight_layout()
        plt.legend()
        plt.show()



        pass


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
