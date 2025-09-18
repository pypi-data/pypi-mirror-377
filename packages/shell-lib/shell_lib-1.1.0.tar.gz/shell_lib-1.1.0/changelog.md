### shell-lib changelog

#### 1.1.0 (2025 Sep 17)

1. Add `sh.is_link(path)` method, check if a path is a symlink.

2. Add `sh.get_file_size(path)` method, get file size.

3. `sh.get_path_info()` returns a `PathInfo` object. Remove `PathInfo.permissions` attribute. Add `.is_readable`, `.is_writable`, `.is_executable` attributes, represents the abilities to the current user.

#### 1.0.3 (2025 Sep 16)

Polish doc and docstrings.

#### 1.0.2 (2025 Sep 15)

1. `sh()` and `sh.safe_run()` always print "Execute:" or "Safely execute:", the `alternative_title=""` can no longer turn off the printing.

2. Print path more clearly.

#### 1.0.1 (2025 Sep 15)

`sh.get_path_info(path)` function returns a `PathInfo` object.

On Windows, `PathInfo.permissions` attribute now is a 1-character `str`, it looks like "7", which only represents the current user is readable, writable, executable.

On other systems, it's still a 3-character `str`, looks like "755".
