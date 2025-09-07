# Custom Regex Engine

A step-by-step project to build a simplified `grep` with regex support from scratch.  

---

### Stage 1: Literal Characters
- Matches **single literal characters** only.  
- Implementation: checks if the given character exists anywhere in the input string.  
- Example:
  ```bash
  echo -n "dog" | ./your_program.sh -E "d"   # exit 0
  echo -n "dog" | ./your_program.sh -E "x"   # exit 1
   ```

---

### Stage 2: Digit Class (`\d`)

- Adds support for `\d` → matches any digit (`0–9`).
- Implementation: uses Python’s str.isdigit() to detect digits in the input.
- Example:

  ```bash
  echo -n "apple123" | ./your_program.sh -E "\d"   # exit 0
  echo -n "apple" | ./your_program.sh -E "\d"      # exit 1
  ```

---