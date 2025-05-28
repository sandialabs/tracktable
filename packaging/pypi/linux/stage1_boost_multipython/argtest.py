import sys

def main():
    print(f"sys.argv has {len(sys.argv)} elements:")
    for (i, arg) in enumerate(sys.argv):
        print(f"element {i}: '{arg}'")
    return 0

if __name__ == '__main__':
    sys.exit(main())