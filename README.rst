MemFs
=====
This is a toy library, don't even think about using it in production!

Usage
-----
The following code snippets show how to interact with the library:

.. code-block::

    import memfs

    # Create a drive
    drive = memfs.create('drive', 'MyDrive')
    # Create a folder (must be inside a drive)
    folder = memfs.create('folder', 'MyFolder', drive.path)
    # Create a file (must be inside a drive/folder/zip)
    file = memfs.create('file', 'MyFile', folder.path)
    memfs.write_to_file(file.path, "The Lord of the Rings")
    # Create a zip archive
    zip = memfs.create('zip', 'MyZip', folder.path)

    # Delete an item (recursively deletes any children)
    memfs.delete(zip.path)

    # Move an item
    memfs.move(file.path, "{}\\{}".format(drive.path, file.name))


Running Tests
-------------
It is recommended to run the tests inside a virtual environment, installing the dependencies from the requirements.txt file:

.. code-block::

    mkvirtualenv memfs # Using virtualenvwrapper in this example
    pip install -r requirements.txt
    pytest