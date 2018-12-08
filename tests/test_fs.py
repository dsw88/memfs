import memfs
from memfs import IllegalFileSystemOperation, PathNotFoundException, PathAlreadyExistsException, InvalidWriteException


def setup_function():
    memfs.index._file_system.reset()


def test_create():
    """
    Create the following file structure and verify its properties:

    Drive1
    |_Folder1
    |_Folder2
      |_Folder3
        |_File1
    |_Zip1
      |_Folder4
      |_File2
    """
    drive_name = 'Drive1'
    drive = memfs.create('drive', drive_name)
    assert drive.type == 'drive'
    assert drive.name == drive_name
    assert drive.path == drive_name
    assert drive.size == 0

    folder1_name = 'Folder1'
    folder1 = memfs.create('folder', folder1_name, drive.path)
    assert folder1.type == 'folder'
    assert folder1.name == folder1_name
    assert folder1.path == "{}\\{}".format(drive.path, folder1_name)
    assert folder1.size == 0

    folder2_name = 'Folder2'
    folder2 = memfs.create('folder', folder2_name, drive.path)
    assert folder2.type == 'folder'
    assert folder2.name == folder2_name
    assert folder2.path == "{}\\{}".format(drive.path, folder2_name)
    assert folder2.size == 0

    folder3_name = 'Folder3'
    folder3 = memfs.create('folder', folder3_name, folder2.path)
    assert folder3.type == 'folder'
    assert folder3.name == folder3_name
    assert folder3.path == "{}\\{}".format(folder2.path, folder3_name)
    assert folder2.size == 0

    file1_name = 'File1'
    file1 = memfs.create('file', file1_name, folder3.path)
    file1_content = 'The Chronicles of Prydain'
    assert drive.size == 0
    memfs.write_to_file(file1.path, file1_content)
    assert file1.type == 'file'
    assert file1.name == file1_name
    assert file1.path == "{}\\{}".format(folder3.path, file1_name)
    assert file1.content == file1_content
    assert folder3.size == 25
    assert folder2.size == 25
    assert drive.size == 25

    zip1_name = 'Zip1'
    zip1 = memfs.create('zip', zip1_name, drive.path)
    assert zip1.type == 'zip'
    assert zip1.name == zip1_name
    assert zip1.path == "{}\\{}".format(drive.path, zip1_name)
    assert zip1.size == 0

    folder4_name = 'Folder4'
    folder4 = memfs.create('folder', folder4_name, zip1.path)
    assert folder4.type == 'folder'
    assert folder4.name == folder4_name
    assert folder4.path == "{}\\{}".format(zip1.path, folder4_name)
    assert folder4.size == 0

    file2_name = 'File2'
    file2 = memfs.create('file', file2_name, zip1.path)
    file2_content = 'The Count of Monte Cristo'
    memfs.write_to_file(file2.path, file2_content)
    assert file2.type == 'file'
    assert file2.name == file2_name
    assert file2.path == "{}\\{}".format(zip1.path, file2_name)
    assert file2.content == file2_content
    assert zip1.size == 13
    assert drive.size == 38

    assert len(drive.children) == 3
    assert len(folder1.children) == 0
    assert len(folder2.children) == 1
    assert len(folder3.children) == 1
    assert len(folder4.children) == 0


def test_write_non_existent_file():
    """
    Writing to a non-existent file raises an error
    """
    drive = memfs.create('drive', "Drive")
    try:
        memfs.write_to_file("{}\\{}".format(drive.path, "FakeFile"), "Foundation")
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathNotFoundException


def test_write_to_non_file():
    """
    Writing content to any non-file object should fail
    """
    drive = memfs.create('drive', "Drive")
    try:
        memfs.write_to_file(drive.path, "Foundation")
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == InvalidWriteException


def test_delete():
    """
    Create and delete the following file structure:

    Drive
    |_Folder
      |_Zip
        |_File
    """
    # Setup
    drive = memfs.create('drive', 'Drive')
    folder = memfs.create('folder', 'Folder', drive.path)
    zip_file = memfs.create('zip', 'Zip', folder.path)
    file = memfs.create('file', 'File', zip_file.path)

    # Test
    assert len(zip_file.children) == 1
    memfs.delete(file.path)
    assert len(zip_file.children) == 0
    assert len(folder.children) == 1
    memfs.delete(zip_file.path)
    assert len(folder.children) == 0
    assert len(drive.children) == 1
    memfs.delete(folder.path)
    assert len(drive.children) == 0
    memfs.delete(drive.path)


def test_non_existent_file():
    """
    Trying to delete a non-existent file returns an error
    """
    try:
        memfs.delete('fake\\path')
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathNotFoundException


def test_create_invalid_path():
    """
    The provided parent path must exist in order to create an object
    """
    try:
        memfs.create('file', 'File', 'some\\nonexistent\\path')
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathNotFoundException


def test_create_duplicate_path():
    """
    Objects cannot be created when an object with the same path already exists
    """
    memfs.create('drive', 'Drive')
    try:
        memfs.create('drive', 'Drive')
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathAlreadyExistsException


def test_drive_root_level():
    """
    Drive objects must be root-level resources
    They cannot be contained in other objects
    """
    drive1 = memfs.create('drive', 'Drive1')
    try:
        memfs.create('drive', 'Drive2', drive1.path)
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == IllegalFileSystemOperation


def test_invalid_root_objects():
    """
    Any non-drive objects may not be root-level objects
    They must be contained in another object (i.e. a drive)
    """
    try:
        memfs.create('file', 'File1')
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == IllegalFileSystemOperation


def test_move_file():
    """
    Test moving a file

    Initial state:

        Drive1
        |_Folder1
          |_File1
        |_Zip1

    Final state:

        Drive1
        |_Folder1
        |_Zip1
          |_File1
    """
    drive = memfs.create('drive', 'Drive1')
    folder1 = memfs.create('folder', 'Folder1', drive.path)
    file1 = memfs.create('file', 'File1', folder1.path)
    zip1 = memfs.create('zip', 'Zip1', drive.path)
    assert len(folder1.children) == 1
    assert len(zip1.children) == 0
    memfs.move(file1.path, "{}\\{}".format(zip1.path, file1.name))
    assert len(folder1.children) == 0
    assert len(zip1.children) == 1
    assert file1.parent.name == zip1.name


def test_move_folder():
    """
    Test moving an entire folder
    Initial state:

        Drive1
        |_Folder1
          |_File1
        |_Zip1

    Final state:

        Drive1
        |_Zip1
          |_Folder1
            |_File1
    """
    drive = memfs.create('drive', 'Drive1')
    folder1 = memfs.create('folder', 'Folder1', drive.path)
    file1 = memfs.create('file', 'File1', folder1.path)
    zip1 = memfs.create('zip', 'Zip1', drive.path)
    assert len(folder1.children) == 1
    assert len(zip1.children) == 0
    memfs.move(folder1.path, "{}\\{}".format(zip1.path, folder1.name))
    assert len(folder1.children) == 1
    assert len(zip1.children) == 1
    assert folder1.parent.name == zip1.name
    assert file1.parent.name == folder1.name


def test_move_non_existent_file():
    """
    Trying to move a non-existent source file should fail with an error
    """
    drive = memfs.create('drive', 'Drive1')
    folder1 = memfs.create('folder', 'Folder1', drive.path)
    try:
        memfs.move("{}\\{}".format(drive.path, "FakeFile"), "{}\\{}".format(drive.path, folder1.name))
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathNotFoundException


def test_move_already_exists_file():
    """
    You can't move a file to a path where one already exists (no overwrites)
    """
    drive = memfs.create('drive', 'Drive1')
    file1 = memfs.create('file', 'File1', drive.path)
    file2 = memfs.create('file', 'File2', drive.path)
    try:
        memfs.move(file1.path, file2.path)
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == PathAlreadyExistsException


def test_move_drive():
    """
    Drives cannot be moved (they must be root entities)
    Should raise an exception
    """
    drive1 = memfs.create('drive', 'Drive1')
    drive2 = memfs.create('drive', 'Drive2')
    try:
        memfs.move(drive2.path, "{}\\{}".format(drive1.path, drive2.name))
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == IllegalFileSystemOperation


def test_move_file_to_root():
    """
    Files cannot be moved to the root
    Should raise an exception
    """
    drive1 = memfs.create('drive', 'Drive1')
    file1 = memfs.create('file',' File1', drive1.path)
    try:
        memfs.move(file1.path, file1.name)
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == IllegalFileSystemOperation


def test_move_file_to_file():
    """
    Files must be leaf nodes and cannot have items moved under them
    """
    drive1 = memfs.create('drive', 'Drive1')
    file1 = memfs.create('file', ' File1', drive1.path)
    file2 = memfs.create('file', 'File2', drive1.path)
    try:
        memfs.move(file1.path, '{}\\{}'.format(file1.path, file2.name))
        assert True == False  # Should not get here
    except Exception as e:
        assert type(e) == IllegalFileSystemOperation
