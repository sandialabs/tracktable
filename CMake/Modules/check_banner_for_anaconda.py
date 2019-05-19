import subprocess
import sys

def to_bytes(my_string):
    if sys.version_info.major == 2:
        return my_string
    elif sys.version_info.major == 3:
        return bytes(my_string.encode())
    else:
        raise RuntimeError("What version of Python is this?")

def capture_banner(executable):
    p = subprocess.Popen([executable, '-i'],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    p.stdin.write(to_bytes('exit()'))
    p.stdin.flush()

    raw_output = p.communicate()[0]

    return str(raw_output)


def main():
    if len(sys.argv) != 2:
        print("usage: {} python_executable".format(sys.argv[0]),
              file=sys.stderr)
        return 1

    banner_message = capture_banner(sys.argv[1])
    if 'conda' in banner_message:
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())

