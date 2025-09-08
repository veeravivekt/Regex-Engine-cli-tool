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


