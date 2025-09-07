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
