---
name: test-writer
description: Use when the user asks to add, write, or improve tests for code. Writes standard-library unittest tests under tests/.
---

# Test writer

1. Use only the standard library `unittest` module. Do not use or import pytest.
2. Put tests in `tests/test_<module>.py`.
3. **Do not modify anything under `shop/`.** If a test exposes a bug, keep the test, mark it
   `@unittest.expectedFailure`, and tell the user about the bug.
4. Run `python3 -m unittest discover -s tests` and make sure it passes before you finish.
