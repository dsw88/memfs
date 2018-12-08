# Expose file system contract methods
from .index import create, delete, move, write_to_file
# Expose file system exceptions.py
from .index import InvalidWriteException, PathNotFoundException, PathAlreadyExistsException, IllegalFileSystemOperation
