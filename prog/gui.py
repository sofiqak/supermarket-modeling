from tkinter import *
from tkinter import font, messagebox, ttk
from modeling import *


class WindowParams:  # Задание параметров пользователем
    def __init__(self, params=None):
        self.result = {}  # Результат ввода пользователя
        self.default_params = params  # Параметры, которые будут стоять в ячейке
        self.continue_state = True  # Статус, что нужно продолжать работу после закрытия окна задания параметров

        self.window = Tk()
        self.window.title('Параметры моделирования')
        self.window.state('zoomed')

        self.custom_font = font.Font(family='ArrialNArrow', size=15)

        self.cur_row, self.width = 0, 20
        self.padx, self.pady = (20, 30), 8

        boxes = {  # Выпадающие списки
            'Шаг моделирования (мин.)': list(range(10, 65, 5)),
            'Число касс': list(range(1, 8)),
            'Максимальная длина очереди': list(range(5, 9))
        }
        self.boxes = {b: self.make_combobox(b, boxes[b]) for b in boxes}

        self.entries = {  # Поля для ввода
            'Промежуток между приходом двух покупателей': {'limits': [1, None], 'unit': 'мин.', 'default': [1, 7]},
            'Время обслуживания покупателя': {'limits': [1, None], 'unit': 'мин.', 'default': [1, 7]},
            'Стоимость покупки': {'limits': [0, None], 'unit': 'руб.', 'default': [30, 9000]},
            'Прибыль от суммы покупки в 1 тыс. р.': {'limits': [0, 100], 'unit': '%', 'default': [9]},
            'Зарплата кассира': {'limits': [0, None], 'unit': 'руб.', 'default': [1500]}
        }
        for title, parameters in self.entries.items():
            if self.default_params and title in self.default_params:
                parameters['default'] = self.default_params[title]
            text = self.get_title(title, parameters['limits'], parameters['unit'])
            self.make_entry_row(text, [parameters])

        # Таблица с затратами
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        self.entries['Затрата на рекламу'] = {'limits': [0, None], 'unit': 'руб.', 'default': [0] * len(days)}
        self.entries['Величина скидки'] = {'limits': [0, 100], 'unit': '%', 'default': [0] * len(days)}
        if self.default_params:
            for header in ['Затрата на рекламу', 'Величина скидки']:
                self.entries[header]['default'] = self.default_params[header]
        self.make_table(['Затрата на рекламу', 'Величина скидки'], days)

        button_frame = Frame(self.window)  # Кнопки внизу
        button_frame.grid(row=self.cur_row, column=1, columnspan=2, sticky='nsew', pady=self.pady)
        for txt, cmd in zip(['Начать моделирование', 'Завершить работу'],
                            [self.process_input, lambda: self.close(False)]):
            Button(button_frame, text=txt, command=cmd, font=self.custom_font, width=self.width).pack(side='left')

    def get_title(self, title, limits, unit):  # Создание заголовка (единицы измерения и пределы)
        cur = ''
        for label, val in zip(['от', 'до'], limits):
            if val is not None:
                cur += f'{label} {val} '
        if unit is not None:
            cur += f'{unit} '
        if cur:
            title += f' ({cur[:-1]})'
        return title

    def make_combobox(self, title, options):  # Создание строки с выпадающим списком
        Label(self.window, text=title, font=self.custom_font).grid(row=self.cur_row, column=0, sticky='w',
                                                                   padx=self.padx, pady=self.pady)
        selected_value = StringVar()
        combobox = ttk.Combobox(self.window, textvariable=selected_value, width=self.width - 2, state='readonly',
                                font=self.custom_font, justify='center')
        combobox['values'] = options
        combobox.grid(row=self.cur_row, column=2, pady=self.pady, padx=self.padx, sticky='w')
        if self.default_params:
            combobox.current(options.index(self.default_params[title][0]))
        else:
            combobox.current(0)
        self.cur_row += 1
        return selected_value

    def make_entry_row(self, title, list_entry):  # Создание строки с полями для ввода
        Label(self.window, text=title, font=self.custom_font).grid(row=self.cur_row, column=0,
                                                                   sticky='w', padx=self.padx)
        start_col = 0
        for entry in list_entry:
            labels = [''] * len(entry['default'])
            if len(labels) == 2:
                labels = ['от', 'до']
            for i, val in enumerate(entry['default']):
                Label(self.window, text=labels[i], font=self.custom_font).grid(row=self.cur_row,
                                                                               column=start_col + 2 * i + 1, sticky='e')
                cell = Entry(self.window, font=self.custom_font)
                cell.config(width=self.width, justify='center', background='white')
                cell.grid(row=self.cur_row, column=start_col + 2 * (i + 1), sticky='w', padx=self.padx, pady=self.pady)
                cell.insert(0, str(val))
                if 'entry' in entry:
                    entry['entry'].append(cell)
                else:
                    entry['entry'] = [cell]
            start_col += len(entry['default']) + 1
        self.cur_row += 1

    def make_table(self, headers, rows):  # Создание строки из полей для ввода
        for i, header in enumerate(headers):
            title = self.get_title(header, self.entries[header]['limits'], self.entries[header]['unit'])
            Label(self.window, text=title, font=self.custom_font).grid(row=self.cur_row, column=2 * i + 1,
                                                                       columnspan=2, padx=self.padx, pady=self.pady)
        default_vals = [self.entries[header]['default'] for header in headers]
        columns = [self.entries[header] for header in headers]
        self.cur_row += 1
        for i, row in enumerate(rows):
            for j, col in enumerate(columns):
                col['default'] = [default_vals[j][i]]
            self.make_entry_row(row, columns)

    def check_row(self):  # Проверка корректности ввода в пустое поле
        result, flag_all_correct = {}, True
        for key, item in self.entries.items():
            vals, flag_cur_correct = [], True
            min_val, max_val = item['limits']
            for i, cell in enumerate(item['entry']):
                try:
                    vals.append(int(cell.get()))
                    if min_val is not None and vals[-1] < min_val or max_val is not None and vals[-1] > max_val:
                        cell.configure(background='red')
                        flag_cur_correct, flag_all_correct = False, False
                    else:
                        if len(item['entry']) == 2 and i == 0:
                            min_val = vals[-1]
                        cell.configure(background='white')
                except Exception:
                    cell.configure(background='red')
                    flag_cur_correct, flag_all_correct = False, False
            result[key] = vals * flag_cur_correct
        return result if flag_all_correct else None

    def process_input(self):  # Процесс ввода, в результате формируются параметры
        result = self.check_row()
        if not result:
            messagebox.showinfo(title='Ошибка', message='Исправьте значения, выделенные красным')
        else:
            self.result = result
            for box in self.boxes:
                self.result[box] = [int(self.boxes[box].get())]
            self.window.destroy()

    def run(self):
        self.window.mainloop()

    def get_result(self):  # -> Параметры
        return self.result

    def close(self, continue_state=True):
        self.continue_state = continue_state
        self.window.destroy()

    def get_continue_state(self):  # Возвращает статус, нужно ли продолжать работу
        return self.continue_state


class WindowExperiment:  # Окно эксперимента
    def __init__(self, params):
        self.experiment = Experiment(params)
        self.continue_state = None  # Статус, нужен ли новый эксперимент
        self.days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        self.window = Tk()
        self.window.title('Моделирование')
        self.window.state('zoomed')
        self.custom_font = font.Font(family='ArrialNarrow', size=15)

        self.time_label = Label(self.window, font=self.custom_font)  # День и время
        self.time_label.grid(row=0, column=0, sticky='w', columnspan=params['Число касс'][0])

        max_que = params['Максимальная длина очереди'][0]
        checkouts = [Frame(self.window, highlightbackground="black", highlightthickness=1)
                     for _ in range(params['Число касс'][0])]
        self.checkouts = []  # Визуализация очередей
        for i, frame in enumerate(checkouts):
            frame.grid(row=1, column=i, rowspan=max_que, sticky='nsew')
            self.checkouts.append([Label(frame, width=10, height=5) for _ in range(max_que)])
            for j, label in enumerate(self.checkouts[-1]):
                label.pack(side='bottom', expand=True)
            Label(self.window, text=f"Касса {i + 1}", font=self.custom_font).grid(row=max_que + 1, column=i)

        # Столбец со статистикой
        Label(self.window, text='Статистика', font=self.custom_font).grid(column=len(self.checkouts), row=0)
        self.stats_labels = {}
        for title, type_cell in zip(['Число обслуженных покупателей', 'Число потерянных (потенциальных) покупателей',
                                     'Средняя длина очереди', 'Среднее время ожидания в очереди (мин.)',
                                     'Средняя занятость касс (%)', 'Общая прибыль'],
                                    ['int', 'int', 'float', 'float', 'float', 'float']):
            self.stats_labels[title] = {'label': Label(self.window, text='', font=self.custom_font), 'type': type_cell}
        for i, key in enumerate(self.stats_labels):
            self.stats_labels[key]['label'].grid(row=i + 1, column=len(self.checkouts), sticky='w', padx=(50, 0))

        button_frame = Frame(self.window)  # Кнопки внизу
        button_frame.grid(row=max(max_que, len(self.stats_labels)) + 2, column=0,
                          columnspan=params['Число касс'][0] + 1, sticky='nsew')
        for txt, cmd in zip(['Следующий шаг', 'Прокрутить до конца', 'Новый эксперимент', 'Завершить работу'],
                            [self.next_step, self.skip_to_end, lambda: self.close(True), self.close]):
            Button(button_frame, text=txt, command=cmd, font=self.custom_font).pack(side='left', fill='x', expand=True)

        self.grid_window()

        self.next_step()  # Визуализация в момент времени 0

    def grid_window(self):  # Разметка окна
        for column in range(len(self.checkouts) + 1):
            self.window.grid_columnconfigure(column, weight=1)
        for row in range(3 + max(len(self.checkouts[0]), len(self.stats_labels))):
            self.window.grid_rowconfigure(row, weight=1)

    def fill_time_label(self, time):  # Заполнение поля с временем
        minute = time % 60
        day, hour = divmod(time // 60, 24)
        self.time_label.config(text=f'{self.days[day]} | {hour}:{minute}')

    def fill_stats_frame(self, stats):  # Заполнение столбца со статистикой
        for key in self.stats_labels:
            label, tp = self.stats_labels[key]['label'], self.stats_labels[key]['type']
            if tp == 'float':
                label.config(text=f'{key}: {"{:.2f}".format(stats[key])}')
            else:
                label.config(text=f'{key}: {stats[key]}')

    def draw_checkouts(self, que_lens):  # Прорисовка очередей
        for i, que_len in enumerate(que_lens):
            for j in range(que_len):
                self.checkouts[i][j].config(bg='lightblue')
            for label in self.checkouts[i][que_len:]:
                label.config(bg='SystemButtonFace')

    def next_step(self):  # Кнопка 'Следующий шаг'
        try:
            time, stats = self.experiment.modeling()
            if stats is not None:
                self.draw_checkouts(stats['que_len'])
                self.fill_stats_frame(stats)
                self.fill_time_label(time)
        except Exception as err:
            messagebox.showinfo(title='Ошибка', message=str(err))

    def skip_to_end(self):  # Кнопка 'Прокрутить до конца'
        try:
            time, stats = self.experiment.modeling()
            if stats is not None:
                while True:
                    cur_time, cur_stats = self.experiment.modeling()
                    if cur_stats is None:
                        self.fill_stats_frame(stats)
                        self.draw_checkouts(stats['que_len'])
                        self.fill_stats_frame(stats)
                        self.fill_time_label(time)
                        break
                    else:
                        time, stats = cur_time, cur_stats
        except Exception as err:
            messagebox.showinfo(title='Ошибка', message=str(err))
            self.close()

    def run(self):
        self.window.mainloop()

    def close(self, flag_continue=False):  # Завершение работы и формирование статуса, нужен ли новый эксперимент
        self.window.destroy()
        self.continue_state = flag_continue

    def get_continue_state(self):  # -> Нужен ли новый эксперимент
        return self.continue_state
