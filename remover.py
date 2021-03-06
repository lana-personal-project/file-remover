import os
import multiprocessing
from multiprocessing.dummy import Pool
import re

import math


class Remover:

    def __init__(self):
        self._working_dir: str = ''
        self._trash_bin: str = ''
        self._remove_size: int = 1
        self._chunk_size: int = 1
        self.set_default_working_dir_and_trash_bin()

    def set_default_working_dir_and_trash_bin(self):
        script_path = os.path.abspath(__file__)
        self._working_dir = os.path.split(script_path)[0]
        self._trash_bin = self._ensure_trash_bin()

    def _ensure_trash_bin(self):
        trash_path = self._working_dir + '_removed'
        if not os.path.exists(trash_path):
            os.mkdir(trash_path)
        return trash_path

    def set_working_dir(self, work_dir: str):
        if os.path.exists(work_dir):
            self._working_dir = work_dir
            self._trash_bin = self._ensure_trash_bin()
        else:
            raise FileExistsError('work_dir not found')

    def set_remove_size(self, remove_size: int):
        if remove_size < 0:
            raise ValueError('remove size must not < 0')
        self._remove_size = remove_size

    def set_chunk_size(self, chunk_size: int):
        if chunk_size < 1:
            raise ValueError('chunk size must at least 1')
        self._chunk_size = chunk_size

    def remove(self):
        threads_pool = self._get_max_size_threads_pool()
        chunks_list = self._get_splited_path_list()

        threads_pool.map(self._move_to_trash, chunks_list)
        threads_pool.close()
        threads_pool.join()

    @staticmethod
    def _get_max_size_threads_pool() -> Pool:
        max_threads = multiprocessing.cpu_count()
        threads_for_other_process = 1
        return Pool(max_threads - threads_for_other_process)

    def _get_splited_path_list(self) -> list:
        files_path = self._get_all_file_path()
        files_path = self._split_path_list(files_path)
        return list(files_path)

    def _get_all_file_path(self) -> list:
        file_list = []
        files = os.listdir(self._working_dir)
        for file in files:
            file_list.append(os.path.join(self._working_dir, file))
        file_list.remove(os.path.abspath(__file__))
        return sorted(file_list)

    def _split_path_list(self, path_list):
        for i in range(0, len(path_list), self._chunk_size):
            yield path_list[i:i + self._chunk_size]

    def _move_to_trash(self, files: list):
        files_len = len(files)
        index_list = self._get_move_index_list(files_len)
        for i in index_list:
            if i < files_len:
                filename = os.path.basename(files[i])
                destination_filename = os.path.join(self._trash_bin, filename)
                destination_filename = self._handle_duplicate(destination_filename)
                os.rename(files[i], destination_filename)
            else:
                return

    def _get_move_index_list(self, number_of_file: int) -> list:
        total_move = self._round(number_of_file * (self._remove_size / self._chunk_size))
        if total_move > 0:
            step = self._round(number_of_file / total_move)
            move_index = 0
            index_list = [move_index]
            for i in range(1, total_move):
                move_index += step
                index_list.append(move_index)
            return index_list
        return []

    @staticmethod
    def _round(val):
        if (float(val) % 1) >= 0.5:
            return math.ceil(val)
        else:
            return round(val)

    @staticmethod
    def _handle_duplicate(path: str) -> str:
        origin_path = path
        suffix = 1
        have_duplicate = os.path.exists(path)
        while have_duplicate:
            suffix += 1
            path = origin_path + '_' + str(suffix)
            have_duplicate = os.path.exists(path)
        return path


def get_remove_size_and_chunk_size_from_input() -> (int, int):
    default = '1/2'
    rate = input('delete rate (remove/chunk_size) (default ' + default + '): ')
    pattern = re.compile('^[1-9]+/[1-9]+')
    if not re.match(pattern, rate.strip()):
        rate = default
    params = rate.split('/')
    remove_size = int(params[0])
    chunk_size = int(params[1])
    print('-> ' + rate)
    return remove_size, chunk_size


remover = Remover()
remove_size, chunk_size = get_remove_size_and_chunk_size_from_input()
remover.set_chunk_size(chunk_size)
remover.set_remove_size(remove_size)
remover.remove()
