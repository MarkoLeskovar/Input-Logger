import os
import shutil
import subprocess

# Main function call
if __name__ == '__main__':

    # Define paths
    cwd = os.path.dirname(__file__)

    # Run PyInstaller through the terminal
    print(f'Running Pyinstaller...')
    subprocess.run('pyinstaller main_app.spec --noconfirm', cwd=cwd)
    print(f'...done!\n')

    # Delete the build directory
    print(f'Removing "build" folder...')
    shutil.rmtree(os.path.join(cwd, 'build'))
    shutil.move(os.path.join(cwd, 'dist'), os.path.join(cwd, os.pardir, 'dist'))
    print(f'...done!\n')