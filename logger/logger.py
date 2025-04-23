import os
import time
import tkinter
import threading
import numpy as np
from io import BytesIO
from PIL import Image, ImageGrab
from pynput import mouse, keyboard

from .database import create_database, SQL_KEY


'''
0-----------------------------------------------------------------------------0
| INPUT LOGGER CLASS                                                          |
0-----------------------------------------------------------------------------0
'''

class InputLogger:

    def __init__(self, output_folder: str, mouse_pos=True, mouse_click=True, mouse_scroll=True, keyboard=True, debug=False):
        self._database = str(output_folder)
        self._track_mouse_pos = bool(mouse_pos)
        self._track_mouse_click = bool(mouse_click)
        self._track_mouse_scroll = bool(mouse_scroll)
        self._track_keyboard = bool(keyboard)
        self._debug = bool(debug)

        # Settings
        self._mouse_threshold_time_ms = 20
        self._mouse_pixel_threshold = 5

        # Initialize values
        self._id = 0
        self._mouse_time = 0
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_dx = 0
        self._mouse_dy = 0
        self._mouse_pixel_threshold_squared = self._mouse_pixel_threshold ** 2
        self._start_time_ms = _get_time_ms()
        self._screen_size = np.asarray([tkinter.Tk().winfo_screenwidth(), tkinter.Tk().winfo_screenheight()])

        # Create a database
        self._data_connection = create_database(self._database)
        self._data_cursor = self._data_connection.cursor()
        self._data_lock = threading.Lock()

        # Initialize listeners
        self._mouse_listener = None
        self._keyboard_listener = None


    # O------------------------------------------------------------------------------O
    # | GETTERS AND SETTERS                                                          |
    # O------------------------------------------------------------------------------O

    @property
    def mouse_pos_sampling_time(self):
        return self._mouse_threshold_time_ms

    @mouse_pos_sampling_time.setter
    def mouse_pos_sampling_time(self, milliseconds):
        self._mouse_threshold_time_ms = int(milliseconds)

    @property
    def mouse_pos_pixel_threshold(self):
        return self._mouse_pixel_threshold

    @mouse_pos_pixel_threshold.setter
    def mouse_pos_pixel_threshold(self, pixels):
        self._mouse_pixel_threshold = int(pixels)
        self._mouse_pixel_threshold_squared = int(pixels) ** 2


    # O------------------------------------------------------------------------------O
    # | SQL DEBUG FUNCTION                                                           |
    # O------------------------------------------------------------------------------O

    def debug_sql(self, query: str):
        self._data_cursor.execute(str(query))
        output = self._data_cursor.fetchall()
        for row in output:
            print(row)


    # O------------------------------------------------------------------------------O
    # | MAIN RUN FUNCTION                                                            |
    # O------------------------------------------------------------------------------O

    # TODO : Add keyboard interrupt exit option!!

    def run(self):

        try:
            # Start mouse listener
            if self._track_mouse_pos or self._track_mouse_click or self._track_mouse_scroll:
                self._mouse_listener = self._create_mouse_listener()
                self._mouse_listener.start()
                if self._debug:
                    print('Started mouse logger')

            # Start keyboard listener
            if self._track_keyboard:
                keyboard_listener = self._create_keyboard_listener()
                keyboard_listener.start()
                if self._debug:
                    print('Started keyboard logger')

            # Check active threads
            while True:
                time.sleep(1)
                # Restart the mouse listener
                if self._mouse_listener is not None:
                    if not self._mouse_listener.is_alive():
                        self._mouse_listener = self._create_mouse_listener()
                        self._mouse_listener.start()
                        if self._debug:
                            print('Re-started mouse logger')
                # Restart the keyboard listener
                if self._keyboard_listener is not None:
                    if not self._keyboard_listener.is_alive():
                        self._keyboard_listener = self._create_keyboard_listener()
                        self._keyboard_listener.start()
                        if self._debug:
                            print('Re-started keyboard logger')

        except KeyboardInterrupt:
            self._stop_listeners()
            self._close_data_connection()
            if self._debug:
                print('Application closed: KeyboardInterrupt')


    def _stop_listeners(self):
        if self._mouse_listener is not None and self._mouse_listener.is_alive():
            self._mouse_listener.stop()
        if self._keyboard_listener is not None and self._keyboard_listener.is_alive():
            self._keyboard_listener.stop()

    def _close_data_connection(self):
        self._data_lock.acquire()
        self._data_cursor.close()
        self._data_connection.close()
        self._data_lock.release()


    # O------------------------------------------------------------------------------O
    # | PRIVATE - MOUSE LISTENER CALLBACKS                                           |
    # O------------------------------------------------------------------------------O

    def _on_mouse_pos(self, x, y):
        x, y = self._clamp_mouse_pos(x, y)
        timestamp = _get_time_ms() - self._start_time_ms

        # Compute difference in mouse movement
        self._mouse_dx = self._mouse_x - x
        self._mouse_dy = self._mouse_y - y

        # Update mouse thresholds
        threshold_pixel = self._mouse_dx ** 2 + self._mouse_dy ** 2 >= self._mouse_pixel_threshold_squared
        threshold_time = timestamp - self._mouse_time >= self._mouse_threshold_time_ms

        # Update mouse movement
        if threshold_pixel and threshold_time:
            # Update timings
            self._mouse_time = timestamp
            self._mouse_x = x
            self._mouse_y = y
            # Add to database
            self._data_lock.acquire()
            self._data_cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (self._id, SQL_KEY.mouse, SQL_KEY.pos, timestamp))
            self._data_cursor.execute("INSERT INTO mouse_pos_events VALUES (?, ?, ?)", (self._id, x, y))
            self._data_connection.commit()
            self._data_lock.release()
            # Update iterator
            self._id += 1
            # Debug
            if self._debug:
                print(f'[{self._id - 1}] - Mouse move = [{x}, {y}], {timestamp} ms')


    def _on_mouse_click(self, x, y, button, pressed):
        x, y = self._clamp_mouse_pos(x, y)
        timestamp = _get_time_ms() - self._start_time_ms
        button = str(button).lstrip('Button.')
        pressed = SQL_KEY.down if pressed else SQL_KEY.up
        # Add to database
        self._data_lock.acquire()
        self._data_cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (self._id, SQL_KEY.mouse, SQL_KEY.click, timestamp))
        self._data_cursor.execute("INSERT INTO mouse_click_events VALUES (?, ?, ?, ?, ?)", (self._id, x, y, button, pressed))
        self._data_connection.commit()
        self._data_lock.release()
        # Update iterator
        self._id += 1
        # Debug
        if self._debug:
            print(f'[{self._id - 1}] - Mouse click = [{x}, {y}], [{button}], [{pressed}], {timestamp} ms')


    def _on_mouse_scroll(self, x, y, dx, dy):
        x, y = self._clamp_mouse_pos(x, y)
        timestamp = _get_time_ms() - self._start_time_ms
        # Add to database
        self._data_lock.acquire()
        self._data_cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (self._id, SQL_KEY.mouse, SQL_KEY.scroll, timestamp))
        self._data_cursor.execute("INSERT INTO mouse_scroll_events VALUES (?, ?, ?, ?)", (self._id, x, y, int(dy)))
        self._data_connection.commit()
        self._data_lock.release()
        # Update iterator
        self._id += 1
        # Debug
        if self._debug:
            print(f'[{self._id - 1}] - Mouse scroll = [{x}, {y}], [{dy}], {timestamp} ms')


    # O------------------------------------------------------------------------------O
    # | PRIVATE - KEYBOARD LISTENER CALLBACKS                                        |
    # O------------------------------------------------------------------------------O

    def _on_key_press(self, key):
        key, key_type = _key_to_string(key)
        timestamp = _get_time_ms() - self._start_time_ms
        if key is not None:
            # Add to database
            self._data_lock.acquire()
            self._data_cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (self._id, SQL_KEY.key, SQL_KEY.down, timestamp))
            self._data_cursor.execute("INSERT INTO keyboard_events VALUES (?, ?, ?)", (self._id, key, key_type))
            self._data_connection.commit()
            self._data_lock.release()
            # Update iterator
            self._id += 1
        # Debug
        if self._debug:
            print(f'[{self._id - 1}] - Key down = [{key}, {key_type}], {timestamp} ms')


    def _on_key_release(self, key):
        key, key_type = _key_to_string(key)
        timestamp = _get_time_ms() - self._start_time_ms
        if key is not None:
            # Add to database
            self._data_lock.acquire()
            self._data_cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (self._id, SQL_KEY.key, SQL_KEY.up, timestamp))
            self._data_cursor.execute("INSERT INTO keyboard_events VALUES (?, ?, ?)", (self._id, key, key_type))
            self._data_connection.commit()
            self._data_lock.release()
            # Update iterator
            self._id += 1
        # Debug
        if self._debug:
            print(f'[{self._id - 1}] - Key up = [{key}, {key_type}], {timestamp} ms')



    # O------------------------------------------------------------------------------O
    # | PRIVATE - AUXILIARY                                                          |
    # O------------------------------------------------------------------------------O

    def _create_mouse_listener(self):
        on_pos = self._on_mouse_pos if self._track_mouse_pos else None
        on_click = self._on_mouse_click if self._track_mouse_click else None
        on_scroll = self._on_mouse_scroll if self._track_mouse_scroll else None
        return mouse.Listener(on_pos, on_click, on_scroll)

    def _create_keyboard_listener(self):
        on_press = self._on_key_press if self._track_keyboard else None
        on_release = self._on_key_release if self._track_keyboard else None
        return keyboard.Listener(on_press, on_release)

    def _clamp_mouse_pos(self, x: int, y: int) -> tuple[int, int]:
        x_clamp = max(0, min(x, self._screen_size[0]))
        y_clamp = max(0, min(y, self._screen_size[1]))
        return x_clamp, y_clamp


'''
0-----------------------------------------------------------------------------0
| AUXILIARY                                                                   |
0-----------------------------------------------------------------------------0
'''

def _grab_screenshot(format='png') -> BytesIO:
    screenshot = ImageGrab.grab()
    buffer = BytesIO()
    screenshot.save(buffer, format=format)
    return buffer

def _get_time_ms():
    return int(time.time() * 1000)

def _key_to_string(key: keyboard.Key | keyboard.KeyCode) -> tuple[str, str] | tuple[None, None]:
    if isinstance(key, keyboard.KeyCode):
        return key.char, SQL_KEY.char
    elif isinstance(key, keyboard.Key):
        return key.name, SQL_KEY.other
    elif not hasattr(key, 'char') and not hasattr(key, 'name'):
        return str(key), SQL_KEY.none
    else:
        return None, SQL_KEY.none
