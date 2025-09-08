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

--

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

