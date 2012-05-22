import subprocess

def run_command(args):
    proc = subprocess.Popen(args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    cout, cerr = proc.communicate()

    return proc.returncode, cout, cerr

