"""
This file contains the code for the MemFs module public contract

Assumptions:
 Concurrency is not a concern (i.e. methods like 'move' don't need to be atomic)
"""
from .filesystem import FileSystem, Drive, Folder, File, Zip, create_object
from .exceptions import IllegalFileSystemOperation, InvalidWriteException, PathNotFoundException, PathAlreadyExistsException

# Only provide a single instance of a file system to consumers of this module
_file_system = FileSystem()


def create(fs_type, name, parent_path=''):
    """
    Create the object in the file system in the given parent path.

    If you are creating a file, you must then use the write_to_file method to put content
    in the file.

    :param fs_type: The type of object being created (i.e. drive, file, etc.)
    :param name: The name of the object to be created.
    :param parent_path: The path of the parent object that will contain this object
    :returns: The created object (i.e. Drive, Folder, etc.)
    :raises PathNotFoundException: The parent path does not exist in the file system
    :raises PathAlreadyExistsException: The path attempting to be created already exists.
    :raises IllegalFileSystemOperationException: The attempted action is not valid
    """
    # Enforce rules about where drives and files can go
    new_path = _get_path(parent_path, name)
    if _get_object(new_path, _file_system):
        raise PathAlreadyExistsException("The requested path to create already exists")

    if fs_type == 'drive':
        if parent_path != '':
            raise IllegalFileSystemOperation('Drives may only be created at the root of the file system')
        parent = _file_system
    else:
        if parent_path == '':
            raise IllegalFileSystemOperation('Only drives may be created at the root of the filesystem')
        parent = _get_object(parent_path, _file_system)
        if not parent:
            raise PathNotFoundException('The requested parent path does not exist')

    # Create and link new file
    new_object = create_object(name, fs_type)
    new_object.parent = parent
    parent.children[new_object.name] = new_object
    return new_object


def delete(path):
    """
    Delete the given object in the file system.

    This method is recursive for objects. If you delete a folder, it and all its children
    will be deleted.

    :param path: The path of the object to delete
    :return: None
    :raises PathNotFoundException: The path attempting to be deleted does not exist
    """
    to_delete = _get_object(path, _file_system)
    if not to_delete:
        raise PathNotFoundException('The requested object does not exist')
    parent = _file_system if to_delete.type == 'drive' else to_delete.parent
    to_delete.parent = None
    del parent.children[to_delete.name]


def move(src, dest):
    """
    Move the given source object to the given destination path

    This functions in a similar manner to os.remove in Python: The 'dest' path is the full
    path to the new location for the filename, not the path to the new parent

    :param src: The source path of the object to move
    :param dest: The destination path to which the object should be moved
    :return: The moved object (i.e. Drive, Folder, etc.)
    :raises PathNotFoundException: The given source path does not exist
    :raises PathAlreadyExistsException: The given destination path already exists.
    :raises IllegalFileSystemOperation: The attempted move action is not valid
    """
    # Source object must exist
    src_object = _get_object(src, _file_system)
    if not src_object:
        raise PathNotFoundException("The given source path does not exist")

    # Cannot move to a path where an object already exists
    if _get_object(dest, _file_system):
        raise PathAlreadyExistsException("The given destination path already exists")

    # Parent object must exist
    dest_parent = _get_parent(dest)
    if not dest_parent:
        raise PathNotFoundException("The given destination parent path does not exist")

    # Drives are only allowed at the root level, and nothing else is allowed at root
    if src_object.type == 'drive':
        raise IllegalFileSystemOperation('Drives may not be moved')
    if dest_parent.path == '':
        raise IllegalFileSystemOperation('You cannot move files, folders, or zips to the root of a file system')

    # Unlink object from file system
    del src_object.parent.children[src_object.name]
    src_object.parent = dest_parent
    dest_parent.children[src_object.name] = src_object


def write_to_file(path, content):
    """
    Write new content to the given file.

    The given file must already exist prior to writing content to the file.

    This action only supports overwriting the existing contents. It does not support
    appending content to the file.

    :param path: The path of the file to write.
    :param content: The content to write to the file.
    :return: The File object just written to.
    :raises PathNotFoundException: The given file path does not exist
    :raises InvalidWriteException: The given object is not a file.
    """
    write_object = _get_object(path, _file_system)

    # The object must exist and be a file
    if not write_object:
        raise PathNotFoundException('The object you are attempting to write does not exist, please create it first')
    if write_object.type != 'file':
        raise InvalidWriteException('The object you are attempting to write is not a file object.')

    write_object.content = content


def _get_path(parent_path, name):
    return name if parent_path == '' else '{}\\{}'.format(parent_path, name)


def _get_parent(path):
    path_parts = path.rsplit('\\', 1)
    if len(path_parts) == 1:
        return _file_system
    return _get_object(path_parts[0], _file_system)


def _get_object(path, parent):
    parts = path.split('\\', 1)
    child = parent.get(parts[0])
    if not child:
        return None
    if len(parts) == 1:
        return child
    return _get_object(parts[1], child)
