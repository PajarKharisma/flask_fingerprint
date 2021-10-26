import os

def allowed_file(filename, allowed_ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext

def empty_dir(dir_name):
    files = os.listdir(dir_name)
    for file in files:
        if file != 'readme.md':
            os.remove('{}/{}'.format(dir_name, file))