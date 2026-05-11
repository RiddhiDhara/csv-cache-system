import hashlib
import os


def get_chunk_size(size):

    if size < 1 * 1024 ** 2:
        return None        # Load whole file
    elif size < 50 * 1024 ** 2:
        return 8192        # 8 KB
    elif size < 500 * 1024 ** 2:
        return 65536       # 64 KB
    elif size < 2 * 1024 ** 3:
        return 262144      # 256 KB
    elif size < 10 * 1024 ** 3:
        return 1048576     # 1 MB
    else:
        return 4194304     # 4 MB


def file_hasher(filePath):

    if not os.path.exists(filePath):
        raise FileNotFoundError(f"File not found: {filePath}")

    size = os.path.getsize(filePath)
    chunk_size = get_chunk_size(size)
    hasher = hashlib.md5()

    with open(filePath, "rb") as file:

        if chunk_size is not None:
            chunk = file.read(chunk_size)

            while len(chunk) > 0:
                hasher.update(chunk)
                chunk = file.read(chunk_size)
        else:
            chunk = file.read()
            hasher.update(chunk)

    return hasher.hexdigest()


