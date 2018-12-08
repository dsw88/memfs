"""
This file contains the code for the MemFs module public contract
"""
import math

# Assumptions:
#  Concurrency is not a concern (i.e. methods like 'move' don't need to be atomic)
#  The only supported interface

class Container:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.parent = None
        self.children = {}

    @property
    def size(self):
        size = 0
        for child_name in self.children:
            child = self.children[child_name]  # TODO - Is there a more Pythonic way to do this?
            size += child.size
        return size

    def get(self, name):
        return self.children.get(name)

    @property
    def path(self):
        if not self.parent:
            raise IllegalFileSystemOperation('The given file object is not present in the file system hierarchy')
        if self.parent.path == '':
            return self.name
        else:
            return "{}\\{}".format(self.parent.path, self.name)


class FileSystem:
    def __init__(self):
        self.children = {}
        self.type = 'filesystem'
        self.path = ''

    def get(self, name):
        return self.children.get(name)


class Drive(Container):
    def __init__(self, name):
        super(Drive, self).__init__(name, 'drive')


class Folder(Container):
    def __init__(self, name):
        super(Folder, self).__init__(name, 'folder')


class Zip(Container):
    def __init__(self, name):
        super(Zip, self).__init__(name, 'zip')

    @property
    def size(self):
        return math.ceil(super(Zip, self).size / 2)


class File():
    def __init__(self, name):
        self.name = name
        self.type = 'file'
        self.parent = None
        self.content = None

    @property
    def size(self):
        if self.content:
            return len(self.content.encode('utf-8'))
        else:
            return 0

    def get(self, name):
        raise IllegalFileSystemOperation('File objects cannot contain other items')

    @property
    def path(self):
        if not self.parent:
            raise IllegalFileSystemOperation('The given file object is not present in the file system hierarchy')
        return "{}\\{}".format(self.parent.path, self.name)


class PathNotFoundException(Exception):
    pass


class PathAlreadyExistsException(Exception):
    pass


class IllegalFileSystemOperation(Exception):
    pass


class InvalidWriteException(Exception):
    pass


# Only provide a single instance of a file system to consumers of this module
_file_system = FileSystem()


def reset():
    _file_system = FileSystem


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
    existing = _get_object("{}\\{}".format(parent_path, name), _file_system)
    if existing:
        raise PathAlreadyExistsException("The requested path to create already exists")
    if fs_type == 'drive':
        if parent_path != '':
            raise IllegalFileSystemOperation('Drives may only be created at the root of the file system')
        new_object = _create_object(name, fs_type)
        new_object.parent = _file_system
        _file_system.children[name] = new_object
    else:
        if parent_path == '':
            raise IllegalFileSystemOperation('Only drives may be created at the root of the filesystem')
        parent = _get_object(parent_path, _file_system)
        if parent.type == 'file':
            raise IllegalFileSystemOperation('Files cannot contain other file system objects')
        new_object = _create_object(name, fs_type)
        new_object.parent = parent
        parent.children[name] = new_object
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
    object_to_delete = _get_object(path, _file_system)
    if not object_to_delete:
        raise PathNotFoundException('The requested object does not exist')
    parent_object = object_to_delete.parent
    object_to_delete.parent = None
    if object_to_delete.type == 'drive':
        del _file_system.children[object_to_delete.name]
    else:  # Is another kind of object
        del parent_object.children[object_to_delete.name]


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
    src_object = _get_object(src, _file_system)
    if not src_object:
        raise PathNotFoundException("The given source path does not exist")
    if _get_object(dest, _file_system):
        raise PathAlreadyExistsException("The given destination path already exists")
    print(dest)

    # TODO - This is ugly
    dest_parts = dest.rsplit('\\', 1)
    if len(dest_parts) == 1:
        dest_parent = _file_system
    else:
        dest_parent = _get_object(dest_parts[0], _file_system)
    if not dest_parent:
        raise PathNotFoundException("The given destination parent path does not exist")

    if src_object.type == 'drive':
        raise IllegalFileSystemOperation('Drives may not be moved')
    if dest_parent.path == '':
        raise IllegalFileSystemOperation('You cannot move files, folders, or zips to the root of a file system')

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
    if not write_object:
        raise PathNotFoundException('The object you are attempting to write does not exist, please create it first')
    if write_object.type != 'file':
        raise InvalidWriteException('The object you are attempting to write is not a file object.')
    write_object.content = content


def _get_object(path, parent):
    parts = path.split('\\', 1)
    child = parent.get(parts[0])
    if not child:
        return None
    if len(parts) == 1:
        return child
    else:
        return _get_object(parts[1], child)


def _create_object(name, fs_type):
    if fs_type == 'file':
        return File(name)
    elif fs_type == 'drive':
        return Drive(name)
    elif fs_type == 'folder':
        return Folder(name)
    elif fs_type == 'zip':
        return Zip(name)
    else:
        raise IllegalFileSystemOperation('You may only create objects of the following types: File, Drive, Folder, Zip')
