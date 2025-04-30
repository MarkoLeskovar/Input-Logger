# Input Logger

`inputlog` is simple input logger app written in Python. It can log your mouse and keyboard input and save it in a local SQL database.  

![app_icon](docs/teaser.png)


## Usage

### How to run the app?

The app is tested and works on Windows 11. Please make sure you have installed the latest version of [Python](https://www.python.org/downloads/) before continuing. Furthermore, it is advisable
to use Python and install modules inside a [virtual environment](https://docs.python.org/3/library/venv.html). Copy the 
following commands into the terminal:   

1. Clone the repository and navigate to the folder.
    ```sh
    git clone https://github.com/MarkoLeskovar/Input-Logger
    cd Input-Logger
   ```

2. Create a virtual environment with a name ".venv".
    ```sh
    python -m venv .venv
    ```

3. Activate virtual environment (on Windows).
    ```sh
   source .venv/Scripts/activate
   ```

4. Activate virtual environment (on Linux).
    ```sh
    source .venv/bin/activate
    ```

5. For local development install `inputlog` in editable mode.
   ```sh
   pip install -e .
   ```

6. Run the app with verbose option [-v].
   ```sh
   inputlog -d output.db -v
   ```

### How to create an executable app?

The app can also be used without installing a Python interpreter or any module. This is achieved thought the use of 
[PyInstaller](https://pyinstaller.org/en/stable/). You can create the executable file yourself by following the 
instructions above and running the [`main_install.py`](install/main_install.py) as follows:
   
   ```sh
   python ./install/main_app.py
   ```


### How to run the app in the background?

The app can also be run as a background process. To do so, copy the following command into the Windows PowerShell 
terminal:
   ```powershell
   Start-Process .\inputlog.exe -WindowStyle Hidden -ArgumentList "-d output.db"
   ```


## Database structure

The data is saved into a local SQLite database, which consist of tables listed bellow. 

- `metadata` - Contains information such as username, operating system and start time.
- `key_ids` - Contains names of abbreviations (key-values pairs) used the SQL tables.
- `events` - Main table consisting of mouse and key events. Details are recorded in:
  - `mouse_pos_events`
  - `mouse_click_events`
  - `mouse_scroll_events`
  - `keyboard_events`

Mouse position `x` and `y` is recorded in pixel screen coordinates, with origin in the top left. Timestamp is recorded 
in milliseconds since the database creation. For more details on possible datatypes and key identifiers,take a look in
[`database.py`](src/inputlog/database.py) file. 

![database_layout](docs/database.png)


## Minimal Python example

The input logger can also be used within the Python code environment as follows:

```python
from inputlog import InputLogger

# Create the logger
logger = InputLogger(
    database='output.db', 
    mouse_pos=True,
    mouse_click=True,
    mouse_scroll=True,
    keyboard=True,
    debug=True
)

# Run until KeyboardInterrupt
logger.run()
```


## Next steps and development ideas

- [ ] Add various analysis scripts
- [ ] Add support for taking screenshots
- [ ] Save results to an online database
