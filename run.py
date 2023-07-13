import subprocess

def run(dir_name: str, server: str|None = None):
    # Run the Flutter application in a separate terminal window.
    if server == 'front' or server == None:
        subprocess.Popen(['flutter', 'run'], cwd=f'./{dir_name}_fe')

    # Run the Python subprocess.
    if server == 'back' or server == None:
        process = subprocess.Popen(['uvicorn', 'app.main:app', '--reload'])
        process.wait()
