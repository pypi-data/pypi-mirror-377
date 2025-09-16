### shell-lib changelog

#### 1.0.3 (2025 Sep 16)

Polish doc and docstrings.

#### 1.0.2 (2025 Sep 15)

1. `sh()` and `sh.safe_run()` always print "Execute:" or "Safely execute:", the `alternative_title=""` can no longer turn off the printing.

2. Print path more clearly.

#### 1.0.1 (2025 Sep 15)

`sh.get_path_info(path)` function returns a `PathInfo` object.

On Windows, `PathInfo.permissions` attribute now is a 1-character `str`, it looks like "7", which only represents the current user is readable, writable, executable.

On other systems, it's still a 3-character `str`, looks like "755".
