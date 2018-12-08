"""
This file contains the file system objects representing things like Zip, File, etc.
"""
import math
from .exceptions import IllegalFileSystemOperation


class Container:
    """
    A mixin-style class that makes an object behave as a container for other file system objects
    """
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.parent = None
        self.children = {}

    @property
    def size(self):
        size = 0
        for _, child in self.children.items():
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

    def reset(self):
        self.children = {}


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


class File:
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

    @property
    def path(self):
        if not self.parent:
            raise IllegalFileSystemOperation('The given file object is not present in the file system hierarchy')
        return "{}\\{}".format(self.parent.path, self.name)

    def get(self, name):
        raise IllegalFileSystemOperation('File objects cannot contain other items')


def create_object(name, fs_type):
    if fs_type == 'file':
        return File(name)
    elif fs_type == 'drive':
        return Drive(name)
    elif fs_type == 'folder':
        return Folder(name)
    elif fs_type == 'zip':
        return Zip(name)
    else:
        raise IllegalFileSystemOperation(
            'You may only create objects of the following types: File, Drive, Folder, Zip')