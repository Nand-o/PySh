import subprocess
import os

commands = [
    'echo "hello world"',
    'echo "|" > pipe_test.txt',
    'echo test1 | findstr test',
    'cd ..',
    'pwd',
    'exit'
]

p = subprocess.Popen(
    ['python', 'pysh.py'], 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE, 
    text=True
)

stdout, stderr = p.communicate("\n".join(commands) + "\n")
print("=== STDOUT ===")
print(stdout)
print("=== STDERR ===")
print(stderr)

if os.path.exists('pipe_test.txt'):
    with open('pipe_test.txt', 'r') as f:
        print("=== CONTENT OF pipe_test.txt ===")
        print(f.read())
