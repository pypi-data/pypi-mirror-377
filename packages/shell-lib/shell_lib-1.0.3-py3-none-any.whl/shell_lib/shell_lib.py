# Co-created with Google Gemini
import os
import re
import sys
import shutil
import stat
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Generator, Union, Optional, overload

PathTypes = Union[str, bytes, Path]
FS_ENCODING = sys.getfilesystemencoding()
IS_WINDOWS = (sys.platform == "win32")

if os.name == 'nt':
    def color(s: str):
        return s
else:
    def color(s: str):
        return f'\033[93m{s}\033[0m'

class PathInfo:
    """
    A class that encapsulates information about a file or directory.
    """
    def __init__(self, path: PathTypes, size: int,
                 ctime: datetime, mtime: datetime, atime: datetime,
                 is_dir: bool, is_file: bool, is_link: bool,
                 permissions: str):
        self.path: str = path.decode(FS_ENCODING) \
                            if isinstance(path, bytes) \
                            else str(path)
        """
        Path, a str object.
        """
        self.size: int = size
        """
        If path is a file, file size.
        If path is a directory, space used by the directory entry itself.
        """
        self.ctime: datetime = ctime
        """
        On Unix-like systems, it's the time of the last metadata change.
        On Windows, it's the creation time.
        """
        self.mtime: datetime = mtime
        """
        Time of last modification.
        """
        self.atime: datetime = atime
        """
        Time of last access.
        """
        self.is_dir: bool = is_dir
        """
        Path is a directory, or a symlink pointing to a directory.
        """
        self.is_file: bool = is_file
        """
        Path is a file, or a symlink pointing to a file.
        """
        self.is_link: bool = is_link
        """
        Path is a symlink.
        """
        self.permissions: str = permissions
        """
        A str object.
        On Unix-like systems, it looks like "777" (3-character).
        On Windows, it looks like "7" (1-character), which only
        represents the current user is readable, writable, executable.
        """

    def __repr__(self):
        s = (f"PathInfo(path={self.path}, size={self.size}, "
             f"ctime={self.ctime}, mtime={self.mtime}, atime={self.atime}, "
             f"is_dir={self.is_dir}, is_file={self.is_file}, is_link={self.is_link}, "
             f"permissions={self.permissions})")
        return s

class CDContextManager:
    def __init__(self, path: Union[PathTypes, None]) -> None:
        self.original_cwd = os.getcwd()
        if path is not None:
            print(color(f"Change directory to: {path!s}"))
            os.chdir(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(color(f"Change directory to: {self.original_cwd}"))
        os.chdir(self.original_cwd)

class Shell:
    """
    Encapsulates file system operations, executing shell commands,
    user interactions, and obtaining runtime information.
    """
    def __setattr__(self, name, _):
        raise AttributeError(f"Can't set attribute {name!r}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if issubclass(exc_type, subprocess.CalledProcessError):
                exit_code = exc_val.returncode
                msg = color(f"\nError: Command failed with exit code {exit_code}")
                print(msg, file=sys.stderr)
            else:
                exit_code = 1

            import traceback
            traceback.print_exception(exc_type, exc_val, exc_tb, file=sys.stderr)
            self.exit(exit_code)

    # --- File and Directory Operations API ---
    def home_dir(self) -> Path:
        """
        Returns the current user's home directory, a pathlib.Path object.
        """
        return Path.home()

    def path(self, path: PathTypes) -> Path:
        """
        Converts a str/bytes path to a pathlib.Path object.
        """
        if isinstance(path, bytes):
            path = path.decode(FS_ENCODING)
        return Path(path)

    def create_dir(self, path: PathTypes, *, exist_ok: bool = False) -> None:
        """
        Creates a directory.

        :param path: The path of the directory to create.
        :param exist_ok: If True, existing directories will not raise an error.
        """
        print(color(f"Create directory: {path!s}"))
        os.makedirs(path, exist_ok=exist_ok)

    def remove_file(self, path: PathTypes, *, ignore_missing: bool = False) -> None:
        """
        Removes a file.

        :param path: The path of the file to remove.
        :param ignore_missing: If True, no error is raised if the file is missing.
        """
        print(color(f"Remove file: {path!s}"))
        if os.path.isdir(path):
            raise IsADirectoryError(f"File path '{path!s}' is a directory.")
        if ignore_missing and not os.path.isfile(path):
            return
        os.remove(path)

    def remove_dir(self, path: PathTypes, *, ignore_missing: bool = False) -> None:
        """
        Recursively removes a directory and its contents.

        :param path: The path of the directory to remove.
        :param ignore_missing: If True, no error is raised if the directory is missing.
        """
        print(color(f"Remove directory: {path!s}"))
        if ignore_missing and not os.path.isdir(path):
            return
        shutil.rmtree(path)

    def clear_dir(self, path: PathTypes) -> None:
        """
        Clear the contents of a directory.

        :param path: The path of the directory to clear.
        """
        print(color(f"Clear directory contents: {path!s}"))
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        shutil.rmtree(entry.path)
                    else:
                        os.unlink(entry.path) # File or symlink
                except FileNotFoundError:
                    continue

    def copy_file(self, src: PathTypes, dst: PathTypes, *, remove_existing_dst: bool = False) -> None:
        """
        Copies a file.

        :param src: The source file path.
        :param dst: The destination file path.
        :param remove_existing_dst: If True, overwrites the destination if it exists.
        """
        print(color(f"Copy file from '{src!s}' to '{dst!s}'"))
        if os.path.isdir(src):
            raise IsADirectoryError(f"Source file '{src!s}' is a directory.")
        if not remove_existing_dst and os.path.isfile(dst):
            raise FileExistsError(f"Destination file '{dst!s}' already exists.")

        shutil.copy2(src, dst) # type: ignore

    def copy_dir(self, src: PathTypes, dst: PathTypes, *, remove_existing_dst: bool = False) -> None:
        """
        Copies a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        :param remove_existing_dst: If True, removes the exist destination before copying.
        """
        print(color(f"Copy directory from '{src!s}' to '{dst!s}'"))
        if os.path.isfile(src):
            raise NotADirectoryError(f"Source directory '{src!s}' is a file.")
        if os.path.isdir(dst):
            if not remove_existing_dst:
                raise FileExistsError(f"Destination directory '{dst!s}' already exists.")
            shutil.rmtree(dst)

        shutil.copytree(src, dst) # type: ignore

    def move_file(self, src: PathTypes, dst: PathTypes, *, remove_existing_dst: bool = False) -> None:
        """
        Moves a file.

        :param src: The source file path.
        :param dst: The destination file path.
        :param remove_existing_dst: If True, overwrites the destination if it exists.
        """
        print(color(f"Move file from '{src!s}' to '{dst!s}'"))
        if os.path.isdir(src):
            raise IsADirectoryError(f"Source file '{src!s}' is a directory.")
        if os.path.isfile(dst):
            if not remove_existing_dst:
                raise FileExistsError(f"Destination file '{dst!s}' already exists.")
            os.remove(dst)

        # Fix bug in Python 3.8-, see bpo-32689.
        if sys.version_info < (3, 9) and isinstance(src, Path):
            src = str(src)

        shutil.move(src, dst) # type: ignore

    def move_dir(self, src: PathTypes, dst: PathTypes, *, remove_existing_dst: bool = False) -> None:
        """
        Moves a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        :param remove_existing_dst: If True, removes the exist destination before moving.
        """
        print(color(f"Move directory from '{src!s}' to '{dst!s}'"))
        if os.path.isfile(src):
            raise NotADirectoryError(f"Source directory '{src!s}' is a file.")
        if os.path.isdir(dst):
            if not remove_existing_dst:
                raise FileExistsError(f"Destination directory '{dst!s}' already exists.")
            shutil.rmtree(dst)

        shutil.move(src, dst) # type: ignore

    def rename_file(self, src: PathTypes, dst: PathTypes) -> None:
        """
        Renames a file.

        :param src: The source file path.
        :param dst: The destination file path.
        """
        print(color(f"Rename file from '{src!s}' to '{dst!s}'"))
        if os.path.isdir(src):
            raise IsADirectoryError(f"Source file '{src!s}' is a directory.")
        if os.path.isdir(dst):
            raise FileExistsError(f"Destination file '{dst!s}' is an existing directory.")
        if os.path.isfile(dst):
            raise FileExistsError(f"Destination file '{dst!s}' already exists.")
        os.rename(src, dst)

    def rename_dir(self, src: PathTypes, dst: PathTypes) -> None:
        """
        Renames a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        """
        print(color(f"Rename directory from '{src!s}' to '{dst!s}'"))
        if os.path.isfile(src):
            raise NotADirectoryError(f"Source directory '{src!s}' is a file.")
        if os.path.isfile(dst):
            raise FileExistsError(f"Destination directory '{dst!s}' is an existing file.")
        if os.path.isdir(dst):
            raise FileExistsError(f"Destination directory '{dst!s}' already exists.")
        os.rename(src, dst)

    def get_path_info(self, path: PathTypes) -> PathInfo:
        """
        Retrieves detailed information about an existing file or directory.

        If the path doesn't exist, raise a FileNotFoundError exception.

        :param path: The path of the file or directory.
        :return: A PathInfo object containing detailed information.
        """
        stats = os.stat(path)
        mode = stats.st_mode

        if IS_WINDOWS:
            value = 0
            if os.access(path, os.R_OK):
                value |= 4
            if os.access(path, os.W_OK):
                value |= 2
            if os.access(path, os.X_OK):
                value |= 1
            permissions = str(value)
        else:
            permissions = oct(mode)[-3:]

        return PathInfo(
            path=path,
            size=stats.st_size,
            ctime=datetime.fromtimestamp(stats.st_ctime),
            mtime=datetime.fromtimestamp(stats.st_mtime),
            atime=datetime.fromtimestamp(stats.st_atime),
            is_dir=stat.S_ISDIR(mode),
            is_file=stat.S_ISREG(mode),
            is_link=os.path.islink(path),
            permissions=permissions
        )

    @overload
    def list_dir(self, path: Union[str, Path]) -> List[str]:
        ...

    @overload
    def list_dir(self, path: bytes) -> List[bytes]:
        ...

    def list_dir(self, path):
        """
        Lists all files and subdirectories within a directory.

        :param path: The directory path.
        :return: A list of all entry names.
        """
        return os.listdir(path)

    @overload
    def walk_dir(self, path: Union[str, Path],
                 top_down: bool = True) -> Generator[Tuple[str, str], None, None]:
        ...

    @overload
    def walk_dir(self, path: bytes,
                 top_down: bool = True) -> Generator[Tuple[bytes, bytes], None, None]:
        ...

    def walk_dir(self, path, top_down = True):
        """
        A generator that traverses a directory and all its subdirectories,
        yielding (directory_path, filename) tuples.

        :param path: The root directory to start walking from.
        :param top_down: Traverse direction.
        :yields: (dirpath, filename) tuples of str or bytes, depending on the input type.
        """
        def _exception(exc):
            print(color(f"sh.walk_dir() failed for path: '{path!s}'"))
            raise exc

        for dirpath, dirnames, filenames in os.walk(path,
                                                    topdown=top_down,
                                                    onerror=_exception):
            for filename in filenames:
                yield (dirpath, filename)

    def cd(self, path: Union[PathTypes, None]):
        """
        Changes the current working directory.

        This method supports to be used as a context manager (`with` statement).
        The original working directory will be restored automatically upon exiting
        the `with` block, even if an exception occurs.

        :param path: The path to the directory to change to.
                     None means no change, using the 'with' statement ensures
                     returning to the current directory.
        """
        return CDContextManager(path)

    def path_exists(self, path: PathTypes) -> bool:
        """
        Checks if a path exists.

        :param path: The file or directory path.
        :return: True if the path exists, False otherwise.
        """
        return os.path.exists(path)

    def is_file(self, path: PathTypes) -> bool:
        """
        Checks if a path is a file, or a symlink pointing to a file.

        :param path: The file path.
        :return: True if the path is a file, False otherwise.
        """
        return os.path.isfile(path)

    def is_dir(self, path: PathTypes) -> bool:
        """
        Checks if a path is a directory, or a symlink pointing to a directory.

        :param path: The directory path.
        :return: True if the path is a directory, False otherwise.
        """
        return os.path.isdir(path)

    def split_path(self, path: PathTypes) -> Union[Tuple[str, str], Tuple[bytes, bytes]]:
        """
        Splits a path into its directory name and file name.

        :param path: The file or directory path.
        :return: A 2-element tuple containing (directory name, file name).
        """
        return os.path.split(path)

    @overload
    def join_path(self, *paths: Union[str, Path]) -> str:
        ...

    @overload
    def join_path(self, *paths: bytes) -> bytes:
        ...

    def join_path(self, *paths):
        """
        Safely joins path components.

        :param paths: Path components to join.
        :return: The joined path string.
        """
        return os.path.join(*paths)

    # --- Shell Command Execution API ---
    def __call__(self,
                 command: str, *,
                 text: bool = True,
                 input: Union[str, bytes, None] = None,
                 timeout: Union[int, float, None] = None,
                 alternative_title: Optional[str] = None,
                 print_output: bool = True,
                 fail_on_error: bool = True) -> subprocess.CompletedProcess:
        """
        Executes a shell command using `shell=True`. Command can use shell
        features like pipe and redirection.

        If command fails, by default, it raises a `subprocess.CalledProcessError`
        exception. For commands that may fail, use `fail_on_error=False`, then check
        the exit-code `ret.returncode`.

        :param command: The command string to execute.
        :param text: If True, output is decoded as text.
        :param input: Data to be sent to the child process.
        :param timeout: Timeout in seconds.
        :param alternative_title: Print this instead of the command.
        :param print_output: If True, streams stdout and stderr to the console.
        :param fail_on_error: If True, raises a subprocess.CalledProcessError on failure.
        :return: A subprocess.CompletedProcess object.
        """
        print(color("Execute:"), command
                                 if alternative_title is None
                                 else alternative_title)
        return subprocess.run(
                command,
                input=input,
                capture_output=not print_output,
                shell=True,
                timeout=timeout,
                check=fail_on_error,
                text=text)

    def safe_run(self,
                 command: List[str], *,
                 text: bool = True,
                 input: Union[str, bytes, None] = None,
                 timeout: Union[int, float, None] = None,
                 alternative_title: Optional[str] = None,
                 print_output: bool = True,
                 fail_on_error: bool = True) -> subprocess.CompletedProcess:
        """
        Executes a command safely, using `shell=False`. Use for commands with
        untrusted external input to prevent shell injection.

        If command fails, by default, it raises a `subprocess.CalledProcessError`
        exception. For commands that may fail, use `fail_on_error=False`, then check
        the exit-code `ret.returncode`.

        :param command: The command as a list of strings (e.g., ['rm', 'file.txt']).
        :param text: If True, output is decoded as text.
        :param input: Data to be sent to the child process.
        :param timeout: Timeout in seconds.
        :param alternative_title: Print this instead of the command.
        :param print_output: If True, streams stdout and stderr to the console.
        :param fail_on_error: If True, raises a subprocess.CalledProcessError on failure.
        :return: A subprocess.CompletedProcess object.
        """
        if not isinstance(command, list):
            raise TypeError("Command must be a list of strings to ensure security.")

        print(color("Safely execute:"), command
                                        if alternative_title is None
                                        else alternative_title)
        return subprocess.run(
                command,
                input=input,
                capture_output=not print_output,
                shell=False,
                timeout=timeout,
                check=fail_on_error,
                text=text)

    # --- Script Control API ---
    def pause(self, msg: Optional[str] = None) -> None:
        """
        Prompts the user to press any key to continue.

        :param msg: The message to print.
        """
        if msg:
            print(color(msg))
        print(color("Press any key to continue..."), end="", flush=True)

        if os.name == 'nt':
            import msvcrt
            msvcrt.getch()
        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        print()

    def ask_choice(self, title: str, *choices: str) -> int:
        """
        Displays a menu and gets a choice from the user.

        :param title: The title for the menu.
        :param choices: The choices as a tuple of strings.
        :return: The 1-based index of the user's choice.
        """
        if not choices:
            raise ValueError("Must have at least one choice.")

        print(color(title))
        for i, choice in enumerate(choices, 1):
            print(color(f"{i}, {choice}"))

        while True:
            answer = input(color("Please choose: "))
            try:
                index = int(answer)
            except ValueError:
                print(color("Invalid input. Please input a number."))
                continue

            if 1 <= index <= len(choices):
                return index
            print(color(f"Invalid choice. Please input a number from 1 to {len(choices)}."))

    def ask_yes_no(self, title: str) -> bool:
        """
        Ask user to answer yes or no.

        :param title: The message to display.
        :return: True for yes, False for no.
        """
        print(color(title))
        while True:
            answer = input(color("Please answer yes(y) or no(n): ")).strip().lower()
            if answer in ("yes", "y"):
                return True
            elif answer in ("no", "n"):
                return False
            print(color("Invalid answer. Please input yes/y/no/n."))

    def ask_regex_input(self, title: str, pattern: str, *,
                        print_pattern: bool = False) -> re.Match:
        """
        Ask user to input a string, and validate it with a regex pattern.

        :param title: The message to display.
        :param pattern: The regex pattern.
        :param print_pattern: Whether to print the regex pattern.
        :return: The re.Match object.
        """
        print(color(title))
        if print_pattern:
            print(color(f"Input for regex: {pattern}"))

        while True:
            answer = input(color("Please input: "))
            m = re.fullmatch(pattern, answer)
            if m:
                return m
            print(color(f"Invalid input. Please input for this regex: {pattern}"))

    def ask_password(self, title: str = "Please input password") -> str:
        """
        Ask user to input a password, which is not echoed on the screen.

        :param title: The message to display, no ":" at the end.
        :return: The password str.
        """
        from getpass import getpass
        title = color(title + ": ")
        return getpass(title)

    def exit(self, exit_code: int = 0) -> None:
        """
        Exits the script with a specified exit code.

        :param exit_code: The exit code, defaults to 0 (no error).
                          Non-zero means an error occurred.
        """
        sys.exit(exit_code)

    def get_username(self) -> str:
        """
        Get the current username.

        On Linux:
        ```
        command              sh.get_username()  sh.home_dir().name
        ./script.py          username           username
        sudo -E ./script.py  root               username
        sudo ./script.py     root               root
        ```
        """
        if os.name == "posix":  # macOS, Linux, etc.
            try:
                import pwd
                uid = os.getuid()
                return pwd.getpwuid(uid).pw_name
            except:
                pass
        elif os.name == "nt":  # Windows
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Volatile Environment')
                username, _ = winreg.QueryValueEx(key, 'USERNAME')
                winreg.CloseKey(key)
                return username
            except:
                pass

        # Fall back to environment variable
        for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
            username = os.environ.get(name)
            if username:
                return username
        raise RuntimeError("Unable to get the current username.")

    def is_elevated(self) -> bool:
        """
        Checks if the script is running with elevated (admin/root) privileges.
        """
        if os.name == "posix": # macOS, Linux, etc.
            return os.geteuid() == 0
        elif os.name == "nt":  # Windows
            try:
                import ctypes
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except:
                pass

        raise RuntimeError(f"Unable to get privilege status.")

    def get_preferred_encoding(self) -> str:
        """
        Returns the preferred encoding for the current locale.

        This is useful for decoding subprocess output or files
        that don't specify an encoding.
        """
        import locale
        try:
            return locale.getpreferredencoding(False)
        except:
            # Fallback for systems where locale module might fail.
            return sys.getdefaultencoding()

    def get_filesystem_encoding(self) -> str:
        """
        Returns the encoding used by the operating system for filenames.
        """
        return FS_ENCODING

    # Operating system constants
    OS_Windows = 1
    OS_Cygwin = 2
    OS_Linux = 4
    OS_macOS = 8
    OS_Unix = 16
    OS_Unix_like = (OS_Linux | OS_macOS | OS_Unix | OS_Cygwin)
    """
    Unix-like systems, currently includes:
    OS_Linux, OS_macOS, OS_Unix, OS_Cygwin
    """

    _CURRENT_OS = None

    @classmethod
    def _get_current_os(cls):
        """
        Internal method to initialize the current operating system value.
        """
        if sys.platform == "win32":
            cls._CURRENT_OS = cls.OS_Windows
        elif sys.platform == "linux":
            cls._CURRENT_OS = cls.OS_Linux
        elif sys.platform == "darwin":
            cls._CURRENT_OS = cls.OS_macOS
        elif sys.platform == "cygwin":
            cls._CURRENT_OS = cls.OS_Cygwin
        else: # Unknown OS
            if os.name == "posix":
                cls._CURRENT_OS = cls.OS_Unix
            else:
                cls._CURRENT_OS = 0

    def is_os(self, os_mask: int) -> bool:
        """
        Test whether it's the operating system specified by the parameter.

        os_mask parameter supports bit OR (|) combination:
        ```
        if sh.is_os(sh.OS_Linux | sh.OS_macOS):
            ...
        elif sh.is_os(sh.OS_Windows):
            ...
        ```

        :param os_mask: Can be sh.OS_Windows, sh.OS_Cygwin, sh.OS_Linux,
                        sh.OS_macOS, sh.OS_Unix, sh.OS_Unix_like.
        """
        if self._CURRENT_OS is None:
            self._get_current_os()
        return bool(os_mask & self._CURRENT_OS) # type: ignore

sh = Shell()