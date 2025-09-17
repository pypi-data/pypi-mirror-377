import time
from bs4 import BeautifulSoup
import requests as req


class ExRandom:
    def __init__(self):# Инициализация генератора случайных чисел с использованием текущего времени в миллисекундах
        seed = int(time.time() * 1000)
        self.seed = seed 

    def tmrand(self):# Возвращает случайное число в диапазоне от 0 до 2**31 - 1

        self.seed = (1103515245 * self.seed + 12345) % (2**31)
        return self.seed 
    
    def rand(self):# Возвращает случайное число в диапазоне от 0 до 1
        return self.tmrand() / (2**31 - 1)
    
    def randint(self, lower_limit, highest_limit):# Возвращает случайное целое число в заданном диапазоне [lower_limit, highest_limit]
        return int(self.rand() * (highest_limit - lower_limit + 1)) + lower_limit

    def lsrand(self,quantity,lower_limit,highest_limit):# Возвращает список случайных целых чисел заданной длины в заданном диапазоне
        listrand = []
        for i in range(quantity):
            listrand.append(self.randint(lower_limit, highest_limit))
        return listrand
    
    def lsrandnul(self,quantity):# Возвращает список из заданного количества экземпляров самого объекта ExRandom
        listrand = []
        for i in range(quantity):
            listrand.append(self.rand())
        return listrand
    
    def randamtrix(self, rows, columns, lower_limit, highest_limit):# Возвращает матрицу случайных целых чисел заданного размера в заданном диапазоне
        matrix = []
        for i in range(rows):
            row = []
            for j in range(columns):
                row.append(self.randint(lower_limit, highest_limit))
            matrix.append(row)
        return matrix
    
    def peprand(self,lower_limit,highest_limit):# Возвращает случайное число в заданном диапазоне, используя данные с сайта countrymeters.info
        response = req.get('https://countrymeters.info/ru/World')
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            number_tag = soup.find('div', id="cp1")
            number = int(number_tag.text.strip().replace(" ", ""))

            self.seed = (1103515245 * self.seed+number + 12345) % (2**31)
            self.seed = (self.seed + lower_limit) % (highest_limit - lower_limit + 1) + lower_limit

        except Exception as e:
            print(f"Error fetching data: {e}")
            
        return self.seed
    
    def bubble_sort(self,arr):
        len_arr = len(arr)
        for i in range(len_arr):
            
            for j in range(i + 1, len_arr):
                if arr[i] > arr[j]:
                    arr[i], arr[j] = arr[j], arr[i]

        return arr

    def selection_sort(self, arr):
        len_arr = len(arr)
        for i in range(len_arr):
            min_index = i

            for j in range(i+1, len_arr):
                if arr[j] < arr[min_index]:
                    min_index = j

            arr[i], arr[min_index] = arr[min_index], arr[i]

        return arr



            
