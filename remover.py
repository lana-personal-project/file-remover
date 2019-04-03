import os
import multiprocessing
from multiprocessing import Pool
from itertools import repeat


def run():
    directory: str = get_containing_dir_from_input()
    trash_bin: str = create_trash_bin(directory)
    files: list = get_all_file_path(directory)

    removing_rate: float = get_removing_rate_from_input()
    threads_pool: Pool = get_max_size_threads_pool()

    threads_pool.starmap(move,
                         zip(repeat(removing_rate),
                             range(1, len(files) + 1),
                             files,
                             repeat(trash_bin)))


def get_containing_dir_from_input():
    is_work_dir_exist = False
    while not is_work_dir_exist:
        path = input('path to folder contains files: ')
        if os.path.exists(path):
            print('-> working directory: ' + path)
            return path


def create_trash_bin(origin_directory):
    trash_path = origin_directory + '_removed'
    if not os.path.exists(trash_path):
        os.mkdir(trash_path)
    return trash_path


def get_all_file_path(path_to_folder):
    file_list = []
    files = os.listdir(path_to_folder)
    for file in files:
        file_list.append(os.path.join(path_to_folder, file))
    return sorted(file_list)


def get_removing_rate_from_input():
    rate = input('delete level (1/x) default x=2: ')
    default = 2
    if rate is not '':
        try:
            rate = float(rate)
            print('-> delete level ' + str(rate) + ' (' + str(100 / rate) + '%)')
            return rate
        except TypeError:
            pass
    print('-> Default: 50%')
    return default


def get_max_size_threads_pool():
    max_threads = multiprocessing.cpu_count()
    threads_for_other_process = 1
    return Pool(max_threads - threads_for_other_process)


def move(rate, index, file, destination):
    if (index % rate) is 0:
        if os.path.exists(file):
            filename = os.path.basename(file)
            destination_filename = os.path.join(destination, filename)
            destination_filename = handle_duplicate(destination_filename)
            os.rename(file, destination_filename)


def handle_duplicate(path):
    origin_path = path
    suffix = 1
    have_duplicate = os.path.exists(path)
    while have_duplicate:
        suffix += 1
        path = origin_path + '_' + str(suffix)
        have_duplicate = os.path.exists(path)
    return path


run()
