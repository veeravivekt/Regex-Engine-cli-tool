import sys

class Token:
    def __init__(self, type_, value=None, chars=None):
        self.type = type_
        self.value = value
        self.chars = chars

def tokenize(pattern: str):
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            nxt = pattern[i + 1]
            if nxt == "d":
                tokens.append(Token("DIGIT"))
            elif nxt == "w":
                tokens.append(Token("WORD"))
            else:
                tokens.append(Token("LITERAL", value=nxt))
            i += 2
            continue
        elif ch == "[":
            j = i + 1
            while j < len(pattern) and pattern[j] != "]":
                j += 1
            if j == len(pattern):
                raise RuntimeError("Unclosed character class")

            body = pattern[i + 1 : j]
            if body.startswith("^"):
                tokens.append(Token("NEG_CLASS", chars=set(body[1:])))
            else:
                tokens.append(Token("POS_CLASS", chars=set(body)))
            i = j + 1
            continue
        elif ch == "^":
            if i == 0:
                tokens.append(Token("START_STRING"))
            else:
                tokens.append(Token("LITERAL", value="^"))
            i += 1
        elif ch == "$":
            if i == len(pattern) - 1:
                tokens.append(Token("END_STRING"))
            else:
                tokens.append(Token("LITERAL", value="$"))
            i += 1
        else:
            tokens.append(Token("LITERAL", value=ch))
            i += 1

    return tokens

def token_matches(tok: Token, ch: str) -> bool:
    if tok.type == "DIGIT":
        return ch.isdigit()
    elif tok.type == "WORD":
        return ch.isalnum() or ch == "_"
    elif tok.type == "POS_CLASS":
        return ch in tok.chars
    elif tok.type == "NEG_CLASS":
        return ch not in tok.chars
    elif tok.type == "LITERAL":
        return ch == tok.value
    return False

def match_from(tokens, input_str, start):
    if start + len(tokens) > len(input_str):
        return False
    for k, tok in enumerate(tokens):
        if not token_matches(tok, input_str[start + k]):
            return False
    return True

def match_pattern(input_line: str, pattern: str) -> bool:
    tokens = tokenize(pattern)

    if not tokens:
        return False

    anchored_start = tokens[0].type == "START_STRING"
    anchored_end = tokens[-1].type == "END_STRING"

    start_idx = 0
    inner_tokens = tokens[1:] if anchored_start else tokens
    if anchored_end:
        inner_tokens = inner_tokens[:-1]

    if anchored_start and anchored_end:
        if len(inner_tokens) != len(input_line):
            return False
        return match_from(inner_tokens, input_line, 0)

    if anchored_start:
        return match_from(inner_tokens, input_line, 0)

    if anchored_end:
        start_idx = len(input_line) - len(inner_tokens)
        if start_idx < 0:
            return False
        return match_from(inner_tokens, input_line, start_idx)

    for start in range(len(input_line) - len(inner_tokens) + 1):
        if match_from(inner_tokens, input_line, start):
            return True
    return False

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "-E":
        print("Usage: ./your_program.sh -E <pattern>", file=sys.stderr)
        sys.exit(1)

    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    print("Logs from your program will appear here!", file=sys.stderr)

    sys.exit(0 if match_pattern(input_line, pattern) else 1)

if __name__ == "__main__":
    main()
