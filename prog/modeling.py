import random
import collections
import numpy as np


class Buyer:  # Покупатель
    def __init__(self, limits_service, limits_buy):
        self.serv_time = random.randint(limits_service[0], limits_service[1])  # Длительность обслуживания
        self.buy = random.randint(limits_buy[0], limits_buy[1])  # Сумма покупки

    def service(self):  # Обслуживание
        if self.serv_time == 0:
            return self.buy
        self.serv_time -= 1
        return None


class Checkout:  # Касса
    def __init__(self):
        self.que = collections.deque()
        self.cur_time = 0  # Текущее время (в минутах)
        self.sum_len = 0  # Суммарная длина очереди
        self.service_time = 0  # Суммарное время обслуживания
        self.service_buyers = 0  # Суммарное число обслуженных покупателей

    def next(self):  # Итерация по минуте
        self.cur_time += 1
        if len(self.que):
            buy = self.que[0].service()
            if buy is not None:
                self.service_buyers += 1
                self.que.popleft()
                if len(self.que):
                    self.que[0].service()
                    self.service_time += 1
                self.sum_len += len(self.que)
                return buy
            else:
                self.service_time += 1
            self.sum_len += len(self.que)
        return None

    def add_buyer(self, buyer):  # Добавление покупателя в очередь
        self.que.append(buyer)

    def get_stats(self):  # Возвращает статистику
        stats = {
            'Число обслуженных покупателей': self.service_buyers,
            'Средняя длина очереди': self.sum_len / max(1, self.cur_time),
            'Среднее время ожидания в очереди (мин.)': (self.sum_len - self.service_time) / max(1, self.service_buyers + len(self.que)),
            'Средняя занятость касс (%)': (self.service_time / max(1, self.cur_time)) * 100
        }
        return stats

    def get_len(self):  # Возвращает длину очереди
        return len(self.que)


class Supermarket:  # Супермаркет
    def __init__(self, cnt_checkouts, max_que, profit_procent, commercial):
        self.max_que = max_que  # Максимальная длина очереди
        self.checkouts = [Checkout() for _ in range(cnt_checkouts)]
        self.profit_coef = profit_procent / 100  # Коэффициент прибыли
        self.profit = 0  # Прибыль
        self.cur_time = 0  # Время
        self.commercial = commercial  # Траты на рекламу, скидки, зп кассирам

    def next(self):  # Итерация по минуте
        day = (self.cur_time // 60) // 24
        for c in self.checkouts:
            buy = c.next()
            if buy is not None:
                self.profit += (1 - self.commercial['Величина скидки'][day] / 100) * buy + self.profit_coef * (buy // 1000)
        if ((self.cur_time + 1) // 60) // 24 != day:  # Конец дня
            self.profit -= self.commercial['Зарплата кассира'][0] * len(self.checkouts)  # зп
            self.profit -= self.commercial['Затрата на рекламу'][day]  # Реклама
        self.cur_time += 1

    def add_buyer(self, buyer):  # Добавление покупателя. Покупатель -> Добавлен ли покупатель
        min_len, min_index = self.max_que, None
        for i, c in enumerate(self.checkouts):
            l = c.get_len()
            if l < min_len:
                min_len, min_index = l, i
        if min_index is None:
            return False
        else:
            self.checkouts[min_index].add_buyer(buyer)
            return True

    def get_stats(self):  # Возвращает накопленную статистику
        stats = {
            'Число обслуженных покупателей': 0,
            'Средняя длина очереди': 0,
            'Среднее время ожидания в очереди (мин.)': 0,
            'Средняя занятость касс (%)': 0
        }
        for c in self.checkouts:
            for key, val in c.get_stats().items():
                stats[key] += val
        for key in stats:
            if key != 'Число обслуженных покупателей':
                stats[key] /= len(self.checkouts)
        stats['Общая прибыль'] = self.profit
        stats['que_len'] = [c.get_len() for c in self.checkouts]  # Длины очередей
        return stats


class Experiment:  # Эксперимент
    def __init__(self, params):
        self.params = params
        self.cur_time = 0
        self.flow_coef = [1., 0.5]  # Коэффициент потока покупатей
        self.is_lost = 0  # Потерян ли покупатель на данный момент
        self.end_time = 7 * 24 * 60  # Конечное время моделирования
        self.lost_buyers = 0  # Число потерянных потенциальных покупателей
        d = {key: params[key] for key in ['Зарплата кассира', 'Затрата на рекламу', 'Величина скидки']}
        self.supermarket = Supermarket(params['Число касс'][0], params['Максимальная длина очереди'][0],
                                       params['Прибыль от суммы покупки в 1 тыс. р.'][0], d)
        self.buyer = Buyer(params['Время обслуживания покупателя'], params['Стоимость покупки'])
        self.buyer_time = 0

    def modeling(self):  # Моделирование процесса
        while self.cur_time < self.end_time:
            if self.cur_time == self.buyer_time:  # Создание покупателя
                self.is_lost = int(not self.supermarket.add_buyer(self.buyer))
                self.lost_buyers += self.is_lost
                self.buyer_time = self.cur_time + self.get_buyer_time()
                self.buyer = Buyer(self.params['Время обслуживания покупателя'], self.params['Стоимость покупки'])
            self.cur_time += 1
            self.supermarket.next()
            if not (self.cur_time - 1) % self.params['Шаг моделирования (мин.)'][0]:  # Вывод статистики
                stats = self.supermarket.get_stats()
                stats['Число потерянных (потенциальных) покупателей'] = self.lost_buyers
                return self.cur_time - 1, stats
        if self.cur_time == self.end_time:  # Докрутка до конца (если шаг моделирования больше оставшегося времени)
            self.cur_time += 1
            stats = self.supermarket.get_stats()
            stats['Число потерянных (потенциальных) покупателей'] = self.lost_buyers
            return self.end_time - 1, stats
        return None, None

    def get_buyer_time(self):  # Генерация времени покупателя
        day, hour = divmod(self.cur_time // 60, 24)
        coef = (self.flow_coef[self.is_lost] *  # Влияние переполненных очередей
                (1. + hour / 24) *  # Влияние часа
                (1. + day / 7 +  # Влияние дня
                 0.1 * (self.params['Затрата на рекламу'][day] // 7000) +
                 0.005 * self.params['Величина скидки'][day]))
        start, end = self.params['Промежуток между приходом двух покупателей']
        mean = (start + end) / 2
        for _ in range(10000):
            ans = int(np.random.normal(mean, coef))
            if start <= ans <= end:
                return ans
        raise Exception('Не удалось сгенерировать время прихода покупателя')
