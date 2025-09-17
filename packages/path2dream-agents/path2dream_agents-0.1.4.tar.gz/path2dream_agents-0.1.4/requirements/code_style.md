# Code quality

- Set up linter for deep checking common issues and run it regulary. Keep the linter output clean - really fix problems, do not hide them.
- Deep issues that would be great to auto-check:
  - unused vars
  - deadcode: do not keep legacy code. This repo is the only user of the code. So if you are removing something - search for usages and really remove outdated code.
  - too complex/long functions/modules.
  - Maximum allowed code file length is 200 lines - decompose longer files.
- Once again: really FIX all problems, do not hide them. For example:
  - if linter produces warning - try to fix it
  - if test fails - do not skip it, fix it. SKIPPING TESTS IS TOTALLY UNACCEPTABLE. All tests should be up-to-date, runnable and really checking something. And really failing if something wrong. NO SKIPPING!
- Maintain repo modularity with Single Responsibility Principle for modules, classes, functions

# Logging:

- Do not over-log, log only essential errors and warning
- Debug logging is allowed during debugging, but clean it up after
- And keep the repo tidy in general - clean up all temp debugging scripts you did.

# Exceptions:

- Fail fast: do not hide warnings under silent try-catch or by silent default meaningless values and behaviour - really think of the source of the exceptions and fix them.
- Do not over-use try-catch: do not catch just to re-raise or log - really try to recover from errors.

# Security

- escape, sanitize, or filter all input and output based on context
- Validate and sanitize file paths to prevent directory traversal attacks
