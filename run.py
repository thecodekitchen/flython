import subprocess
import os

def run(server:str):
    dir = os.getcwd()
    dir_name = os.path.basename(dir)

    if server == 'back':
        subprocess.run(['uvicorn', 'app.main:app', '--reload'])

    if server == 'front':
        subprocess.run(['flutter', 'run'], cwd = f'./{dir_name}_fe')