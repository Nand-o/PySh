import os
from typing import List
from .parser import CommandSegment
from .executor import execute_segment, execute_builtin, is_builtin, execute_single_command_windows

def execute_pipeline(segments: List[CommandSegment]) -> bool:
    if not segments:
        return True
        
    # Validasi segment kosong
    if any(not seg.args and not seg.redirects for seg in segments):
        print("pysh: syntax error near unexpected token '|'")
        return True

    # Jika hanya 1 command (tanpa pipe)
    if len(segments) == 1:
        seg = segments[0]
        if not seg.args:
            return True
            
        # Builtins tanpa pipe langsung jalan di parent
        if is_builtin(seg.args[0]):
            return execute_builtin(seg.args)
            
        if not hasattr(os, 'fork'):
            return execute_single_command_windows(seg)
            
        try:
            pid = os.fork()
        except OSError as e:
            print(f"pysh: fork failed: {e}")
            return True
            
        if pid == 0:
            execute_segment(seg)
        else:
            os.waitpid(pid, 0)
        return True

    # Multi-pipe
    if not hasattr(os, 'fork'):
        print("pysh: piping not yet fully supported on Windows")
        return True

    num_pipes = len(segments) - 1
    pipes = [os.pipe() for _ in range(num_pipes)]
    pids = []

    for i in range(len(segments)):
        try:
            pid = os.fork()
        except OSError as e:
            print(f"pysh: fork failed: {e}")
            break

        if pid == 0:
            if i > 0:
                os.dup2(pipes[i-1][0], 0)
            if i < num_pipes:
                os.dup2(pipes[i][1], 1)
            
            for p in pipes:
                os.close(p[0])
                os.close(p[1])
            
            execute_segment(segments[i])
        else:
            pids.append(pid)

    for p in pipes:
        os.close(p[0])
        os.close(p[1])

    for pid in pids:
        os.waitpid(pid, 0)
        
    return True
