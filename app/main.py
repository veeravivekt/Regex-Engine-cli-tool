import sys

class Token:
    def __init__(self, type_, value=None, chars=None):
        self.type = type_
        self.value = value
        self.chars = chars

def _split_alternatives(segment: str):
    parts = []
    current = []
    paren_depth = 0
    bracket_depth = 0
    i = 0
    while i < len(segment):
        ch = segment[i]
        if ch == "\\" and i + 1 < len(segment):
            current.append(segment[i])
            current.append(segment[i + 1])
            i += 2
            continue
        if ch == "[":
            bracket_depth += 1
        elif ch == "]" and bracket_depth > 0:
            bracket_depth -= 1
        elif ch == "(":
            paren_depth += 1
        elif ch == ")" and paren_depth > 0:
            paren_depth -= 1
        elif ch == "|" and paren_depth == 0 and bracket_depth == 0:
            parts.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    parts.append("".join(current))
    return parts

def tokenize(pattern: str, state=None):
    if state is None:
        state = {"next_group_id": 1}
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            nxt = pattern[i + 1]
            if nxt == "d":
                tokens.append(Token("DIGIT"))
                i += 2
                continue
            elif nxt == "w":
                tokens.append(Token("WORD"))
                i += 2
                continue
            elif nxt.isdigit():
                j = i + 1
                while j < len(pattern) and pattern[j].isdigit():
                    j += 1
                tokens.append(Token("BACKREF", value=int(pattern[i + 1 : j])))
                i = j
                continue
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
        elif ch == "(":
            j = i + 1
            depth = 1
            while j < len(pattern) and depth > 0:
                if pattern[j] == "\\" and j + 1 < len(pattern):
                    j += 2
                    continue
                if pattern[j] == "[":
                    k = j + 1
                    while k < len(pattern) and pattern[k] != "]":
                        if pattern[k] == "\\" and k + 1 < len(pattern):
                            k += 2
                            continue
                        k += 1
                    j = k + 1
                    continue
                if pattern[j] == "(":
                    depth += 1
                elif pattern[j] == ")":
                    depth -= 1
                j += 1 
            if depth != 0:
                raise RuntimeError("Unclosed group")
            body = pattern[i + 1 : j - 1]
            alts = _split_alternatives(body)
            gid = state["next_group_id"]
            state["next_group_id"] += 1
            tokens.append(Token("CAPTURE_START", value=gid))
            if len(alts) == 1:
                tokens.extend(tokenize(alts[0], state))
            else:
                alt_tokens = [tokenize(alt, state) for alt in alts]
                tokens.append(Token("ALTERNATION", value=alt_tokens))
            tokens.append(Token("CAPTURE_END", value=gid))
            i = j
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
        elif ch == "+":
            if tokens and tokens[-1].type not in ("START_STRING", "END_STRING", "ONE_OR_MORE", "ZERO_OR_ONE", "ZERO_OR_MORE"):
                prev = tokens.pop()
                tokens.append(Token("ONE_OR_MORE", value=prev))
            else:
                tokens.append(Token("LITERAL", value="+"))
            i += 1
        elif ch == ".":
            tokens.append(Token("ANY"))
            i += 1
        elif ch == "?":
            if tokens and tokens[-1].type not in ("START_STRING", "END_STRING", "ONE_OR_MORE", "ZERO_OR_ONE", "ZERO_OR_MORE"):
                prev = tokens.pop()
                tokens.append(Token("ZERO_OR_ONE", value=prev))
            else:
                tokens.append(Token("LITERAL", value="?"))
            i += 1
        elif ch == "*":
            if tokens and tokens[-1].type not in ("START_STRING", "END_STRING", "ONE_OR_MORE", "ZERO_OR_ONE", "ZERO_OR_MORE"):
                prev = tokens.pop()
                tokens.append(Token("ZERO_OR_MORE", value=prev))
            else:
                tokens.append(Token("LITERAL", value="*"))
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
    elif tok.type == "ANY":
        return ch != "\n"
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

def match_tokens(tokens, input_str, start_index, must_end_at_eos, capture_start_idx_stack=None, captures=None):

    def dfs(token_index, input_index, capture_start_idx_stack=capture_start_idx_stack, captures=captures):
        if capture_start_idx_stack is None:
            capture_start_idx_stack = []
        if captures is None:
            captures = {}
        if token_index == len(tokens):
            return (input_index == len(input_str)) if must_end_at_eos else True

        tok = tokens[token_index]

        if tok.type == "ALTERNATION":
            remainder = tokens[token_index + 1 :]
            for alt in tok.value:
                combined = alt + remainder
                if match_tokens(combined, input_str, input_index, must_end_at_eos, capture_start_idx_stack, captures):
                    return True
            return False

        if tok.type == "CAPTURE_START":
            return dfs(token_index + 1, input_index, capture_start_idx_stack + [input_index], captures.copy())

        if tok.type == "CAPTURE_END":
            gid = tok.value
            if not capture_start_idx_stack:
                return False
            start_idx = capture_start_idx_stack[-1]
            new_captures = captures.copy()
            new_captures[gid] = input_str[start_idx:input_index]
            return dfs(token_index + 1, input_index, capture_start_idx_stack[:-1], new_captures)

        if tok.type == "BACKREF":
            ref = tok.value
            if ref not in captures:
                return False
            ref_text = captures[ref]
            end_index = input_index + len(ref_text)
            if input_str[input_index:end_index] == ref_text:
                return dfs(token_index + 1, end_index, capture_start_idx_stack, captures)
            return False

        if tok.type == "ONE_OR_MORE":
            base = tok.value
            j = input_index
            count = 0
            while j < len(input_str) and token_matches(base, input_str[j]):
                j += 1
                count += 1
            if count == 0:
                return False
            for used in range(count, 0, -1):
                if dfs(token_index + 1, input_index + used, capture_start_idx_stack, captures):
                    return True
            return False

        if tok.type == "ZERO_OR_ONE":
            base = tok.value
            if input_index < len(input_str) and token_matches(base, input_str[input_index]):
                if dfs(token_index + 1, input_index + 1, capture_start_idx_stack, captures):
                    return True
            return dfs(token_index + 1, input_index, capture_start_idx_stack, captures)

        if tok.type == "ZERO_OR_MORE":
            base = tok.value
            j = input_index
            while j < len(input_str) and token_matches(base, input_str[j]):
                j += 1
            for used in range(j - input_index, -1, -1):
                if dfs(token_index + 1, input_index + used, capture_start_idx_stack, captures):
                    return True
            return False

        if input_index >= len(input_str):
            return False
        if not token_matches(tok, input_str[input_index]):
            return False
        return dfs(token_index + 1, input_index + 1, capture_start_idx_stack, captures)

    return dfs(0, start_index)

def match_pattern(input_line: str, pattern: str) -> bool:
    tokens = tokenize(pattern)

    if not tokens:
        return False

    anchored_start = tokens[0].type == "START_STRING"
    anchored_end = tokens[-1].type == "END_STRING"

    inner_tokens = tokens[1:] if anchored_start else tokens
    if anchored_end:
        inner_tokens = inner_tokens[:-1]

    if anchored_start and anchored_end:
        return match_tokens(inner_tokens, input_line, 0, True)

    if anchored_start:
        return match_tokens(inner_tokens, input_line, 0, False)

    if anchored_end:
        for start in range(0, len(input_line) + 1):
            if match_tokens(inner_tokens, input_line, start, True):
                return True
        return False

    for start in range(0, len(input_line) + 1):
        if match_tokens(inner_tokens, input_line, start, False):
            return True
    return False

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "-E":
        print("Usage: ./your_program.sh -E <pattern> [file]", file=sys.stderr)
        sys.exit(1)

    pattern = sys.argv[2]

    if len(sys.argv) >= 4:
        file_paths = sys.argv[3:]
        multi_file = len(file_paths) > 1
        any_matched = False
        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception as e:
                print(str(e), file=sys.stderr)
                sys.exit(1)
            for raw_line in lines:
                test_line = raw_line[:-1] if raw_line.endswith("\n") else raw_line
                if match_pattern(test_line, pattern):
                    if multi_file:
                        print(f"{file_path}:{raw_line}", end="")
                    else:
                        print(raw_line, end="")
                    any_matched = True
        sys.exit(0 if any_matched else 1)
    else:
        input_line = sys.stdin.read()
        print("Logs from your program will appear here!", file=sys.stderr)
        sys.exit(0 if match_pattern(input_line, pattern) else 1)

if __name__ == "__main__":
    main()
