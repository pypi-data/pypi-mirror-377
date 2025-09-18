import os
import errno
import shutil
import hashlib
import logging

from pydantic import validate_call

from ..constants import WarnEnum, HashAlgoEnum, MAX_PATH_LENGTH


logger = logging.getLogger(__name__)


@validate_call
def create_dir(create_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG) -> None:
    """Create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str, required): Create directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                        Defaults to 'DEBUG'.

    Raises:
        ValueError: If `create_dir` argument length is out of range.
        OSError   : When warning mode is set to ERROR and directory already exists.
        OSError   : If failed to create directory.
    """

    create_dir = create_dir.strip()
    if (len(create_dir) < 1) or (MAX_PATH_LENGTH < len(create_dir)):
        raise ValueError(
            f"`create_dir` argument length {len(create_dir)} is out of range, "
            f"must be between 1 and {MAX_PATH_LENGTH} characters!"
        )

    if not os.path.isdir(create_dir):
        try:
            _message = f"Creating '{create_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            os.makedirs(create_dir)
        except OSError as err:
            if (err.errno == errno.EEXIST) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{create_dir}' directory already exists!")
            else:
                logger.error(f"Failed to create '{create_dir}' directory!")
                raise

        _message = f"Successfully created '{create_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.info(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.EEXIST, f"'{create_dir}' directory already exists!")

    return


@validate_call
def remove_dir(remove_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG) -> None:
    """Remove directory if `remove_dir` exists.

    Args:
        remove_dir (str, required): Remove directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                        Defaults to 'DEBUG'.

    Raises:
        ValueError: If `remove_dir` argument length is out of range.
        OSError   : When warning mode is set to ERROR and directory doesn't exist.
        OSError   : If failed to remove directory.
    """

    remove_dir = remove_dir.strip()
    if (len(remove_dir) < 1) or (MAX_PATH_LENGTH < len(remove_dir)):
        raise ValueError(
            f"`remove_dir` argument length {len(remove_dir)} is out of range, "
            f"must be between 1 and {MAX_PATH_LENGTH} characters!"
        )

    if os.path.isdir(remove_dir):
        try:
            _message = f"Removing '{remove_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            shutil.rmtree(remove_dir)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{remove_dir}' directory doesn't exist!")
            else:
                logger.error(f"Failed to remove '{remove_dir}' directory!")
                raise

        _message = f"Successfully removed '{remove_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.info(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{remove_dir}' directory doesn't exist!")

    return


@validate_call
def remove_dirs(remove_dirs: list[str], warn_mode: WarnEnum = WarnEnum.DEBUG) -> None:
    """Remove directories if `remove_dirs` exist.

    Args:
        remove_dirs (List[str], required): Remove directory paths as list.
        warn_mode   (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                                Defaults to 'DEBUG'.
    """

    for _remove_dir in remove_dirs:
        remove_dir(remove_dir=_remove_dir, warn_mode=warn_mode)

    return


@validate_call
def remove_file(file_path: str, warn_mode: WarnEnum = WarnEnum.DEBUG) -> None:
    """Remove file if `file_path` exists.

    Args:
        file_path (str, required): Remove file path.
        warn_mode (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                        Defaults to 'DEBUG'.

    Raises:
        ValueError: If `file_path` argument length is out of range.
        OSError   : When warning mode is set to ERROR and file doesn't exist.
        OSError   : If failed to remove file.
    """

    file_path = file_path.strip()
    if (len(file_path) < 1) or (MAX_PATH_LENGTH < len(file_path)):
        raise ValueError(
            f"`file_path` argument length {len(file_path)} is out of range, "
            f"must be between 1 and {MAX_PATH_LENGTH} characters!"
        )

    if os.path.isfile(file_path):
        try:
            _message = f"Removing '{file_path}' file..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            os.remove(file_path)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{file_path}' file doesn't exist!")
            else:
                logger.error(f"Failed to remove '{file_path}' file!")
                raise

        _message = f"Successfully removed '{file_path}' file."
        if warn_mode == WarnEnum.ALWAYS:
            logger.info(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{file_path}' file doesn't exist!")

    return


@validate_call
def remove_files(file_paths: list[str], warn_mode: WarnEnum = WarnEnum.DEBUG) -> None:
    """Remove files if `file_paths` exist.

    Args:
        file_paths (List[str], required): Remove file paths as list.
        warn_mode  (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                                Defaults to 'DEBUG'.
    """

    for _file_path in file_paths:
        remove_file(file_path=_file_path, warn_mode=warn_mode)

    return


@validate_call
def get_file_checksum(
    file_path: str,
    hash_method: HashAlgoEnum = HashAlgoEnum.md5,
    chunk_size: int = 4096,
    warn_mode: WarnEnum = WarnEnum.DEBUG,
) -> str | None:
    """Get file checksum.

    Args:
        file_path   (str         , required): Target file path.
        hash_method (HashAlgoEnum, optional): Hash method. Defaults to `HashAlgoEnum.md5`.
        chunk_size  (int         , optional): Chunk size. Defaults to 4096.
        warn_mode   (str         , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                                Defaults to 'DEBUG'.

    Raises:
        ValueError: If `file_path` argument length is out of range.
        ValueError: If `chunk_size` argument value is invalid.
        OSError   : When warning mode is set to ERROR and file doesn't exist.

    Returns:
        str | None: File checksum or None if file doesn't exist.
    """

    file_path = file_path.strip()
    if (len(file_path) < 1) or (MAX_PATH_LENGTH < len(file_path)):
        raise ValueError(
            f"`file_path` argument length {len(file_path)} is out of range, "
            f"must be between 1 and {MAX_PATH_LENGTH} characters!"
        )

    if chunk_size < 10:
        raise ValueError(
            f"`chunk_size` argument value {chunk_size} is invalid, must be greater than 10!"
        )

    _file_checksum: str | None = None
    if os.path.isfile(file_path):
        _file_hash = hashlib.new(hash_method.value)
        with open(file_path, "rb") as _file:
            while True:
                _file_chunk = _file.read(chunk_size)
                if not _file_chunk:
                    break
                _file_hash.update(_file_chunk)

        _file_checksum = _file_hash.hexdigest()
    else:
        _message = f"'{file_path}' file doesn't exist!"
        if warn_mode == WarnEnum.ALWAYS:
            logger.warning(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)
        elif warn_mode == WarnEnum.ERROR:
            raise OSError(errno.ENOENT, _message)

    return _file_checksum


__all__ = [
    "create_dir",
    "remove_dir",
    "remove_dirs",
    "remove_file",
    "remove_files",
    "get_file_checksum",
]
