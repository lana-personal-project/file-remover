import os
import multiprocessing
from multiprocessing import Pool
import re
from itertools import repeat


class Remover:

    def __init__(self):
        self.containing_dir = self._get_containing_dir()
        self.threads_pool = self._get_max_size_threads_pool()

    @staticmethod
    def _get_containing_dir() -> str:
        return os.getcwd()

    @staticmethod
    def _get_max_size_threads_pool() -> Pool:
        max_threads = multiprocessing.cpu_count()
        threads_for_other_process = 1
        return Pool(max_threads - threads_for_other_process)

    def remove(self):
        remove_size, chunks_size = self.get_remove_size_and_chunk_size_from_input()
        trash_bin: str = self.create_trash_bin()
        chunks_list = self.get_splited_path_list(chunks_size)

    def get_remove_size_and_chunk_size_from_input(self) -> (int, int):
        default = '1/2'
        rate = input('delete level (remove/chunk_size) (default ' + default + '): ')
        pattern = re.compile('^[1-9]+/[1-9]+')
        if not re.match(pattern, rate.strip()):
            rate = default
        params = rate.split('/')
        remove_size = int(params[0])
        chunk_size = int(params[1])
        return remove_size, chunk_size

    def get_splited_path_list(self, split_range) -> list:
        files_path = self._get_all_file_path(self.containing_dir)
        self._split_path_list(files_path, split_range)
        return files_path

    @staticmethod
    def _get_all_file_path(path_to_folder) -> list:
        file_list = []
        files = os.listdir(path_to_folder)
        for file in files:
            file_list.append(os.path.join(path_to_folder, file))
        file_list.remove(os.path.abspath(__file__))
        return sorted(file_list)

    @staticmethod
    def _split_path_list(path_list, split_range):
        for i in range(0, len(path_list), split_range):
            yield path_list[i:i + split_range]

    def create_trash_bin(self):
        trash_path = self.containing_dir + '_removed'
        if not os.path.exists(trash_path):
            os.mkdir(trash_path)
        return trash_path

    def move(self, number: int, files: list, destination: str):
        index_list = self._get_move_index_list(number, len(files))
        for i in index_list:
            destination_filename = os.path.join(destination, files[i])
            destination_filename = self._handle_duplicate(destination_filename)
            os.rename(files[i], destination_filename)

    def _get_move_index_list(self, number: int, max_len: int) -> list:
        step = round(max_len / number) + 1
        move_index = 0
        index_list = [move_index]
        for i in range(1, number):
            move_index += step
            index_list.append(move_index)
        return move_index

    def _handle_duplicate(self, path: str) -> str:
        origin_path = path
        suffix = 1
        have_duplicate = os.path.exists(path)
        while have_duplicate:
            suffix += 1
            path = origin_path + '_' + str(suffix)
            have_duplicate = os.path.exists(path)
        return path
