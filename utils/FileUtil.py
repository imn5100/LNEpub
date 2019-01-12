# -*- coding: utf-8 -*-
import os
import zipfile


def zip_path(input_path, out_put):
    f = zipfile.ZipFile(out_put, 'w', zipfile.ZIP_DEFLATED)
    file_list = []
    dfs_get_zip_file(input_path, file_list)
    for fi in file_list:
        f.write(fi)
    f.close()
    return out_put


def dfs_get_zip_file(input_path, result):
    files = os.listdir(input_path)
    for fi in files:
        if os.path.isdir(input_path + '/' + fi):
            dfs_get_zip_file(input_path + '/' + fi, result)
        else:
            result.append(input_path + '/' + fi)
