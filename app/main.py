import sys

def match_pattern(input_line, pattern):
    if pattern == r'\d':
        return any(char.isdigit() for char in input_line)
    elif pattern == r'\w':
        return any(char.isalnum() or char == '_' for char in input_line)
    elif len(pattern) == 1:
            return pattern in input_line
    else:
        raise RuntimeError(f"Unhandled pattern: {pattern}")


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    print("Logs from your program will appear here!", file=sys.stderr)

    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()