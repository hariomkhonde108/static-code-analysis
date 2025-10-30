1. Which issues were the easiest to fix, and which were the hardest? Why?
- Easiest: style issues (naming, docstrings, f-strings) — these are mechanical changes.
- Hardest: design issues like global state and eval use — they require restructuring (class encapsulation) and safe parsing choices.

2. Did the static analysis tools report any false positives?
- Not in the provided pylint excerpt. Some style warnings (missing docstrings) can be noisy but are legitimate. If a small script intentionally uses globals for simplicity, the global warning could be a false positive relative to intent.

3. How would you integrate static analysis into workflow?
- Run linters locally (pre-commit hooks) and in CI pipelines (GitHub Actions) to fail PRs that introduce new warnings or errors. Configure rule sets per project and provide autofix where safe. Use gating for high-severity issues only or fail-fast for critical security issues.

4. Tangible improvements observed after fixes
- Better input validation and explicit exceptions improved robustness.
- Eliminating eval and using safe parsing reduces security risk.
- Encapsulation (InventorySystem) removes globals, improving testability and readability.
- Using context managers and encoding makes file I/O more portable and correct.