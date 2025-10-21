# Custom Regex Engine

A step-by-step project to build a simplified `grep` with regex support from scratch.  

---

### Step 1: Literal Characters
- Matches **single literal characters** only.  
- Implementation: checks if the given character exists anywhere in the input string.  
- Example:
  ```bash
  echo -n "dog" | ./your_program.sh -E "d"   # exit 0
  echo -n "dog" | ./your_program.sh -E "x"   # exit 1
   ```

---

### Step 2: Digit Class (`\d`)

- Adds support for `\d` → matches any digit (`0–9`).
- Implementation: uses Python’s str.isdigit() to detect digits in the input.
- Example:

  ```bash
  echo -n "apple123" | ./your_program.sh -E "\d"   # exit 0
  echo -n "apple" | ./your_program.sh -E "\d"      # exit 1
  ```

---

### Step 3: Word Class (`\w`)
- Adds support for `\w` → matches any “word” character (`[A-Za-z0-9_]`).  
- **Implementation:** checks `char.isalnum() or char == '_'` over the input string.  
- **Example:**
  ```bash
  echo -n "__"        | ./your_program.sh -E "\w"   # exit 0
  echo -n "hello123"  | ./your_program.sh -E "\w"   # exit 0
  echo -n "!!!"       | ./your_program.sh -E "\w"   # exit 1

---

### Step 4: Character Classes (`[abc]`)
- Adds support for **character classes** → matches any single character listed inside square brackets.  
- **Implementation:** checks if any character from the input exists in the set `pattern[1:-1]`.  
- **Limitations:** only simple sets like `[abc]` are supported (no ranges like `[a-z]`, no negation `[^abc]`, no escaping yet).  
- **Example:**
  ```bash
  echo -n "cat" | ./your_program.sh -E "[abc]"   # exit 0 (matches 'c' or 'a')
  echo -n "dog" | ./your_program.sh -E "[abc]"   # exit 1 (no match)

---

### Step 5: Negative Character Classes (`[^abc]`)
- Adds support for **negative character classes** → matches any character **not** listed inside the brackets.  
- **Implementation:** detects a leading `^` inside `[ ]` and succeeds if the input contains at least one character **not in** the given set.  
- **Limitations:** only simple sets like `[^abc]` are supported (no ranges like `[^a-z]`, no escaping yet).  

- **Examples:**
```bash
  echo -n "cat"  | ./your_program.sh -E "[^abc]"   # exit 0 (matches 't' since it's not a, b, or c)
  echo -n "cab"  | ./your_program.sh -E "[^abc]"   # exit 1 (all chars are in a, b, or c)
  echo -n "zzz"  | ./your_program.sh -E "[^abc]"   # exit 0 (matches 'z')
```

- **Edge Cases:**

  - **Empty input (`""`)** → no characters to test, so it does **not match**.
  - **`[^]` (empty negated set)** → matches **any character**, since no characters are excluded.
  - **Newlines from stdin** (`echo` without `-n`) may count as characters — be consistent with earlier steps.

---

### Step 6: Combining Character Classes
- Adds support for **patterns that combine multiple tokens** (`\d`, `\w`, `[abc]`, `[^abc]`, and literals) in sequence.  
- **Implementation:** the pattern is first tokenized into a list of matchers, then the input string is scanned **character by character** to check if the entire sequence appears consecutively at any position.  
- **Notes:**
  - Spaces in the pattern are treated as **literal spaces** (important for matching phrases like `\d apple`).  
  - Matching is done left-to-right; the whole token sequence must succeed for a match.  
  - Still limited to exact sequences — quantifiers (`+`, `*`, `?`) and wildcards (`.`) are **not yet supported**.

- **Examples:**
```bash
  echo -n "1 apple"     | ./your_program.sh -E "\d apple"      # exit 0 (digit + space + "apple")
  echo -n "1 orange"    | ./your_program.sh -E "\d apple"      # exit 1 (does not match "apple")
  echo -n "100 apples"  | ./your_program.sh -E "\d\d\d apple"  # exit 0 (three digits + " apple")
  echo -n "3 dogs"      | ./your_program.sh -E "\d \w\w\ws"    # exit 0 (digit + space + 3 word chars + "s")
  echo -n "4 cats"      | ./your_program.sh -E "\d \w\w\ws"    # exit 0 (digit + space + 3 word chars + "s")
  echo -n "1 dog"       | ./your_program.sh -E "\d \w\w\ws"    # exit 1 (missing the "s")
```

* **Edge Cases:**

  * Pattern longer than input → always fails.
  * Empty pattern → not supported (raises error or always false).
  * Input with trailing newline (`\n`) from `stdin.read()` may affect matches unless stripped.

---

### Step 7: Start Anchor (`^`)
- Adds support for the **start-of-string anchor** `^`.
- **Behavior:** when a pattern starts with `^`, it matches only if the rest of the pattern occurs at the very beginning of the input string. It does not consume a character by itself.
- **Implementation:**
  - Tokenizer emits a special start token only if `^` appears at the beginning of the pattern.
  - Matching is attempted only from index `0` when anchored.
  - A `^` found elsewhere in the pattern is treated as a literal `^`.
- **Notes:**
  - `^` inside a character class (e.g., `[^abc]`) still means negation and is unaffected by this step.
  - Single-line input only; start-of-line equals start-of-string here.

- **Examples:**
```bash
echo -n "log"     | ./your_program.sh -E "^log"           # exit 0 (starts with "log")
echo -n "logs"    | ./your_program.sh -E "^log"           # exit 0 (starts with "log")
echo -n "slog"    | ./your_program.sh -E "^log"           # exit 1 (does not start with "log")
echo -n "123abc"  | ./your_program.sh -E "^[\d][\d][\d]" # exit 0 (three digits at start)
```

---



### Step 8: End Anchor (`$`)
- Adds support for the **end-of-string anchor** `$`.
- **Behavior:** when a pattern ends with `$`, it matches only if the preceding part of the pattern ends exactly at the end of the input string. `$` does not consume a character by itself.
- **Implementation:**
  - Tokenizer emits a special end token only if `$` appears at the end of the pattern.
  - When end-anchored, matching is aligned to the end of the input.
  - A `$` found elsewhere in the pattern is treated as a literal `$`.
- **Combining anchors:** You can combine `^` and `$` (e.g., `^dog$`) to require the entire string matches exactly.
- **Notes:** Single-line input only; end-of-line equals end-of-string here.

- **Examples:**
```bash
echo -n "dog"       | ./your_program.sh -E "dog$"        # exit 0 (ends with "dog")
echo -n "hotdog"    | ./your_program.sh -E "dog$"        # exit 0 (ends with "dog")
echo -n "dogs"      | ./your_program.sh -E "dog$"        # exit 1 (does not end with "dog")
echo -n "abc123"    | ./your_program.sh -E "[\d][\d][\d]$" # exit 0 (three digits at end)
echo -n "abc123@"   | ./your_program.sh -E "\w\w\w$"    # exit 1 (does not end with 3 word chars)
echo -n "abc123cde" | ./your_program.sh -E "\w\w\w$"    # exit 0 (three word chars at end)
echo -n "dog"       | ./your_program.sh -E "^dog$"       # exit 0 (exact match)
```

---

## Step 9: One-or-More Quantifier (`+`)
- Adds support for the **greedy one-or-more** quantifier `+`.
- **Behavior:** the `+` applies to the immediately preceding element (literal, `\d`, `\w`, or character class) and requires it to match one or more times, consuming as many as possible before allowing the rest of the pattern to match.
- **Implementation:**
  - Tokenizer wraps the preceding token into a `ONE_OR_MORE` token when encountering `+`.
  - The matcher uses greedy consumption with backtracking when followed by additional tokens or anchors.
  - If there is no valid preceding token (e.g., pattern starts with `+`), `+` is treated as a literal plus.
- **Examples:**
```bash
echo -n "apple"     | ./your_program.sh -E "a+"        # exit 0 (one 'a')
echo -n "SaaS"      | ./your_program.sh -E "a+"        # exit 0 (two 'a')
echo -n "dog"       | ./your_program.sh -E "a+"        # exit 1 (no 'a')
echo -n "cats"      | ./your_program.sh -E "ca+ts"     # exit 0 (one 'a')
echo -n "caats"     | ./your_program.sh -E "ca+ts"     # exit 0 (two 'a')
echo -n "cts"       | ./your_program.sh -E "ca+ts"     # exit 1 (needs ≥1 'a')
echo -n "123"       | ./your_program.sh -E "\d+"       # exit 0 (three digits)
echo -n "abc123"    | ./your_program.sh -E "\d+$"      # exit 0 (digits at end)
echo -n "123abc"    | ./your_program.sh -E "^\d+"      # exit 0 (digits at start)
```

---

### Step 10: Zero-or-One Quantifier (`?`)
- Adds support for the **optional** quantifier `?`.
- **Behavior:** the `?` applies to the immediately preceding element and allows it to appear either once or not at all (greedy: prefers one when possible).
- **Implementation:**
  - Tokenizer wraps the preceding token into a `ZERO_OR_ONE` token when encountering `?`.
  - The matcher tries to consume one occurrence if it matches; otherwise it proceeds with zero.
  - If there is no valid preceding token (e.g., pattern starts with `?`), `?` is treated as a literal question mark.
- **Examples:**
```bash
echo -n "dog"     | ./your_program.sh -E "dogs?"     # exit 0 (zero 's')
echo -n "dogs"    | ./your_program.sh -E "dogs?"     # exit 0 (one 's')
echo -n "dogss"   | ./your_program.sh -E "dogs?"     # exit 1 (two 's')
echo -n "cat"     | ./your_program.sh -E "dogs?"     # exit 1 (doesn't match "dog")
echo -n "color"   | ./your_program.sh -E "colou?r"   # exit 0 (zero 'u')
echo -n "colour"  | ./your_program.sh -E "colou?r"   # exit 0 (one 'u')
echo -n "5"       | ./your_program.sh -E "\d?"        # exit 0 (one digit)
echo -n ""        | ./your_program.sh -E "\d?"        # exit 0 (zero digits)
```

---

### Step 11: Wildcard (`.`)
- Adds support for the **wildcard** character `.` which matches any single character except a newline.
- **Behavior:** each `.` consumes exactly one character. Useful as a placeholder.
- **Implementation:** tokenizer emits an `ANY` token; matcher accepts any non-newline character for it.
- **Examples:**
```bash
echo -n "dog" | ./your_program.sh -E "d.g"   # exit 0 (matches 'o')
echo -n "dag" | ./your_program.sh -E "d.g"   # exit 0 (matches 'a')
echo -n "d9g" | ./your_program.sh -E "d.g"   # exit 0 (matches '9')
echo -n "cog" | ./your_program.sh -E "d.g"   # exit 1 (doesn't start with 'd')
echo -n "dg"  | ./your_program.sh -E "d.g"   # exit 1 (requires one middle char)
echo -n "cat" | ./your_program.sh -E "..."   # exit 0 (three dots)
echo -n "a1b" | ./your_program.sh -E ".\d." # exit 0 (any, digit, any)
```

---

### Step 12: Alternation (`|`) and Grouping (`( )`)
- Adds support for alternation between multiple subpatterns using `|`, grouped inside parentheses.
- **Behavior:** `(cat|dog)` matches either "cat" or "dog". Alternation can include more than two options: `(red|blue|green)`.
- **Implementation:** groups are parsed, split on top-level `|` into alternatives, and each alternative is tokenized and tried in order.
- **Examples:**
```bash
echo -n "cat"        | ./your_program.sh -E "(cat|dog)"       # exit 0
echo -n "dog"        | ./your_program.sh -E "(cat|dog)"       # exit 0
echo -n "apple"      | ./your_program.sh -E "(cat|dog)"       # exit 1
echo -n "doghouse"   | ./your_program.sh -E "(cat|dog)"       # exit 0 (matches "dog")
echo -n "I like cats"| ./your_program.sh -E "I like (cats|dogs)" # exit 0
echo -n "blue"       | ./your_program.sh -E "(red|blue|green)" # exit 0
```

---

### Step 13: Capturing Groups and Backreferences (`( )` and `\1`)
- Adds support for a single capturing group and a single backreference `\1`.
- **Behavior:** parentheses create a capture of the matched substring; `\1` must match the exact same text later in the pattern.
- **Implementation:** the engine records the substring matched by the first group and compares it against `\1` when encountered. Works with alternation and other tokens.
- **Examples:**
```bash
echo -n "cat and cat" | ./your_program.sh -E "(cat) and \1"   # exit 0
echo -n "cat and dog" | ./your_program.sh -E "(cat) and \1"   # exit 1
echo -n "cat and cat" | ./your_program.sh -E "(\w+) and \1"  # exit 0
echo -n "dog and dog" | ./your_program.sh -E "(\w+) and \1"  # exit 0
echo -n "cat and dog" | ./your_program.sh -E "(\w+) and \1"  # exit 1
echo -n "123-123"     | ./your_program.sh -E "(\d+) - \1"    # exit 0 (with spaces)
```

---

### Step 14: Multiple Capturing Groups and Backreferences (`\1`, `\2`, ...)
- Extends backreference support to multiple groups and references.
- **Behavior:** each pair of parentheses defines an incrementing group number; `\1`, `\2`, ... must match exactly what their corresponding group matched previously.
- **Examples:**
```bash
echo -n "3 red and 3 red"     | ./your_program.sh -E "(\d+) (\w+) and \1 \2"      # 0
echo -n "3 red and 4 red"     | ./your_program.sh -E "(\d+) (\w+) and \1 \2"      # 1
echo -n "3 red and 3 blue"    | ./your_program.sh -E "(\d+) (\w+) and \1 \2"      # 1
echo -n "cat and dog are dog and cat" | ./your_program.sh -E "(cat) and (dog) are \2 and \1" # 0
echo -n "foo-bar-foo-bar"     | ./your_program.sh -E "(\w+)-(\w+)-\1-\2"          # 0
```

---


### Step 15: Nested Capturing Groups and Backreferences
- Adds support documentation for nested capturing groups and how their backreferences are numbered.
- **Numbering rules:**
  - Groups are numbered by the position of their opening parenthesis from left to right.
  - The outer group gets the earlier number; inner groups get numbers as they appear.
  - `\N` refers to the Nth group’s exact matched text.
- **Examples:**
```bash
echo -n "'cat and cat' is the same as 'cat and cat'" | ./your_program.sh -E "('(cat) and \2') is the same as \1" # 0
echo -n "dog-dog" | ./your_program.sh -E "((dog)-\2)"                                                         # 0
echo -n "cat cat and cat cat" | ./your_program.sh -E "((\w+) \2) and \1"                                      # 0
```

---

### Step 17: File Search (Multi-line Files)
- Extends file searching to handle multi-line files.
- **Behavior:**
  - Reads the file line by line.
  - Prints every line that matches the pattern (full line).
  - Exits with code 0 if any line matched; 1 if none matched.
- **Examples:**
```bash
echo "banana" > fruits.txt
echo "grape" >> fruits.txt
echo "blackberry" >> fruits.txt
echo "blueberry" >> fruits.txt

./your_program.sh -E ".*berry" fruits.txt
# prints:
blackberry
blueberry

./your_program.sh -E "carrot" fruits.txt
# prints nothing, exit 1
```

---

### Step 18: Searching Multiple Files
- Extends file search to multiple files, printing matching lines prefixed with the filename.
- **Behavior:**
  - Processes each file independently.
  - Prints `filename:line` for each matching line when multiple files are provided.
  - Exits with code 0 if any match across all files; 1 otherwise.
- **Examples:**
```bash
echo "banana" > fruits.txt
echo "blueberry" >> fruits.txt
echo "broccoli" > vegetables.txt
echo "carrot" >> vegetables.txt

./your_program.sh -E "b.*$" fruits.txt vegetables.txt
# prints:
fruits.txt:banana
fruits.txt:blueberry
vegetables.txt:broccoli

./your_program.sh -E "missing_fruit" fruits.txt vegetables.txt
# prints nothing, exit 1
```

---

### Step 19: Recursive Search (`-r`)
- Adds support for recursive search through directories when `-r` is provided.
- **Behavior:**
  - Walks the provided directories recursively using the filesystem order.
  - Prints `path/to/file:line` for each matching line.
  - Exits with code 0 if any match across all files; 1 otherwise.
- **Examples:**
```bash
mkdir -p dir/subdir
echo "pear" > dir/fruits.txt
echo "strawberry" >> dir/fruits.txt
echo "celery" > dir/subdir/vegetables.txt
echo "carrot" >> dir/subdir/vegetables.txt
echo "cucumber" > dir/vegetables.txt
echo "corn" >> dir/vegetables.txt

./your_program.sh -r -E ".*er" dir/
# dir/fruits.txt:strawberry
# dir/subdir/vegetables.txt:celery
# dir/vegetables.txt:cucumber

./your_program.sh -r -E ".*ar" dir/
# dir/fruits.txt:pear
# dir/subdir/vegetables.txt:carrot
```

---