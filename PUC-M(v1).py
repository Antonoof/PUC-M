import flet as ft
import base64
import cv2
import numpy as np

# Загружаем каскадный классификатор
face_cascade = cv2.CascadeClassifier('face.xml')


# создаем суперкласс для покадровой передачи камеры для игры flying head
class flying_head(ft.UserControl):
    def __init__(self):
        super().__init__()

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        # количество отжиманий для лвл
        k = 0
        # расстояние в прямоугольниках
        length_line = 5
        length_gap = 5
        # сохранение старых переменных, для взрыва
        x1 = 0
        y1 = 0
        w1 = 0
        h1 = 0
        # время для анимации
        t = 0
        # для определения начала игры
        s = 0
        # таймер для выключения камеры
        countdown = 13
        # чтение камеры
        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            # frame = cv2.resize(frame,(600,600))
            # переворачиваем камеру для зеркального эффекта
            frame = cv2.flip(frame, 1)
            # фильтр от засветов
            saturated_frame = cv2.convertScaleAbs(frame, alpha=1, beta=-2)
            # конвертируем в черно-белый
            gray = cv2.cvtColor(saturated_frame, cv2.COLOR_BGR2GRAY)

            # находим лицо
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))

            # проверка на отсутствие лица
            if len(faces) == 0 and s > 12:
                # Если лица не обнаружены, выводим количество секунд на экране
                cv2.putText(saturated_frame, f"Осталось: {countdown}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)
                countdown -= 1

                if countdown < 0:
                    # Когда счетчик достигнет 0, закрываем окно, камеру и героя
                    container.content.controls.pop()
                    container.update()
                    break
            else:
                countdown = 13

            # рисуем квадратик
            for (x, y, w, h) in faces:
                #12
                if s >= 12:
                    # отображение героя
                    hero = ft.Container(
                        ft.Image(
                            src=f"vor.png",
                            width=140,
                            height=120),
                        margin=ft.margin.only(left=900, top=int(y)+250)
                    )
                    container.content.controls.append(hero)
                    container.update()
                    container.content.controls.pop()

                # ожидание отжимания вниз
                if y > 240 and s < 7:
                    s += 1
                # ожидание отжимания вверх
                if y < 80 and s < 13 and s > 6:
                    s += 1
            # взрыв динамита
            if s >= 12 and t > 8:
                # если старая координата совпадает с новой
                if x1+w1 > int(x) and x1-w1 < int(x) and y1+h1 > int(y) and y1-h1 < int(y):
                    container.content.controls.pop()
                    container.update()
                    break
                # запись новых переменных
                x1 = int(x)
                y1 = int(y)
                w1 = int(w)
                h1 = int(h)
                t = 0
                # количество отжим
                k+=1
            # если игра началась, то рисуем динамит и ограничения для взрыва
            elif s >= 12:
                if k<15:
                    t += 0.2
                    color = (int((1 - t) * 255), 0, int(t * 255/4))
                    cv2.putText(saturated_frame, f'{8-t:.1f}', (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                color, 2)
                    cv2.putText(saturated_frame, 'Level: easy', (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 162, 242), 2)
                    # Рисование пунктирного прямоугольника
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1), (i + length_line, y1), color, 2)

                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1 + h1), (i + length_line, y1 + h1), color, 2)

                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1, i), (x1, i + length_line), color, 2)

                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1 + w1, i), (x1 + w1, i + length_line), color, 2)

                    # Рисуем "динамит"
                    cv2.rectangle(saturated_frame, (int(x1 + w1*0.4), int(y1 + h1*0.4)), (int(x1 + w1*0.6), int(y1 +h1*0.8)), color, -1)

                    # Рисуем фитиль
                    fuse_length = int((8 - t) * 10)  # Меняем эту строку, чтобы контролировать длину фитиля
                    cv2.line(saturated_frame, (int(x1 + w1*0.5), int(y1 + h1*0.4)), (int(x1 + w1*0.5), int(y1 +h1*0.41)-fuse_length), color, 2)

                    # Рисуем искру для фитиля
                    cv2.ellipse(saturated_frame, (int(x1 + w1*0.5), int(y1 +h1*0.41)-fuse_length), (10, 5), 0, 200, 360, (0, 255, 255), 2)
                elif k < 30:
                    t += 0.4
                    color = (int((1 - t) * 255), 0, int(t * 255 / 4))
                    cv2.putText(saturated_frame, f'{8 - t:.1f}', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                color, 2)
                    cv2.putText(saturated_frame, 'Level: good', (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 162, 242), 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1), (i + length_line, y1), color, 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1 + h1), (i + length_line, y1 + h1), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1, i), (x1, i + length_line), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1 + w1, i), (x1 + w1, i + length_line), color, 2)
                    cv2.rectangle(saturated_frame, (int(x1 + w1 * 0.4), int(y1 + h1 * 0.4)),
                                  (int(x1 + w1 * 0.6), int(y1 + h1 * 0.8)), color, -1)
                    fuse_length = int((8 - t) * 10)  # Меняем эту строку, чтобы контролировать длину фитиля
                    cv2.line(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.4)),
                             (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), color, 2)

                    cv2.ellipse(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), (10, 5), 0,
                                200, 360, (0, 255, 255), 2)
                elif k < 60:
                    t += 0.5
                    color = (int((1 - t) * 255), 0, int(t * 255 / 4))
                    cv2.putText(saturated_frame, f'{8 - t:.1f}', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                color, 2)
                    cv2.putText(saturated_frame, 'Level: perfect', (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 162, 242), 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1), (i + length_line, y1), color, 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1 + h1), (i + length_line, y1 + h1), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1, i), (x1, i + length_line), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1 + w1, i), (x1 + w1, i + length_line), color, 2)
                    cv2.rectangle(saturated_frame, (int(x1 + w1 * 0.4), int(y1 + h1 * 0.4)),
                                  (int(x1 + w1 * 0.6), int(y1 + h1 * 0.8)), color, -1)
                    fuse_length = int((8 - t) * 10)  # Меняем эту строку, чтобы контролировать длину фитиля
                    cv2.line(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.4)),
                             (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), color, 2)

                    cv2.ellipse(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), (10, 5), 0,
                                200, 360, (0, 255, 255), 2)
                else:
                    t += 0.8
                    color = (int((1 - t) * 255), 0, int(t * 255 / 4))
                    cv2.putText(saturated_frame, f'{8 - t:.1f}', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                color, 2)
                    cv2.putText(saturated_frame, 'Level: insane', (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 162, 242), 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1), (i + length_line, y1), color, 2)
                    for i in range(x1, x1 + w1, length_line + length_gap):
                        cv2.line(saturated_frame, (i, y1 + h1), (i + length_line, y1 + h1), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1, i), (x1, i + length_line), color, 2)
                    for i in range(y1, y1 + h1, length_line + length_gap):
                        cv2.line(saturated_frame, (x1 + w1, i), (x1 + w1, i + length_line), color, 2)
                    cv2.rectangle(saturated_frame, (int(x1 + w1 * 0.4), int(y1 + h1 * 0.4)),
                                  (int(x1 + w1 * 0.6), int(y1 + h1 * 0.8)), color, -1)
                    fuse_length = int((8 - t) * 10)  # Меняем эту строку, чтобы контролировать длину фитиля
                    cv2.line(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.4)),
                             (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), color, 2)
                    cv2.ellipse(saturated_frame, (int(x1 + w1 * 0.5), int(y1 + h1 * 0.41) - fuse_length), (10, 5), 0,
                                200, 360, (0, 255, 255), 2)



            # этап : начальное положение
            if s < 13:
                # начальная точка, конечная точка, цвет, толщина
                cv2.line(saturated_frame, (190, 420), (240, 420), (0, 0, 255), 2)
                cv2.line(saturated_frame, (420, 420), (470, 420), (0, 0, 255), 2)
                cv2.line(saturated_frame, (215, 395), (215, 445), (0, 0, 255), 2)
                cv2.line(saturated_frame, (445, 395), (445, 445), (0, 0, 255), 2)
                cv2.putText(saturated_frame, "waiting for the game to start...", (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)
            #  обновление фрейма
            _, im_arr = cv2.imencode('.png', saturated_frame)
            im_b64 = base64.b64encode(im_arr)
            self.img.src_base64 = im_b64.decode("utf-8")
            self.update()

    def build(self):
        # вывод во flet
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20)
        )
        return self.img


# создаем суперкласс для покадровой передачи камеры для игры отжимания
class push_up(ft.UserControl):
    def __init__(self):
        super().__init__()

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        t = 0
        # количество отжиманий
        k = 0
        # состояние
        c = 0
        # для определения начала игры
        s = 0
        # таймер для выключения камеры
        countdown = 13
        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            # frame = cv2.resize(frame,(600,600))
            # переворачиваем камеру для зеркального эффекта
            frame = cv2.flip(frame, 1)
            # фильтр от засветов
            saturated_frame = cv2.convertScaleAbs(frame, alpha=1, beta=-2)
            # конвертируем в черно-белый
            gray = cv2.cvtColor(saturated_frame, cv2.COLOR_BGR2GRAY)

            # находим лицо
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))

            # проверка на отсутствие лица
            if len(faces) == 0 and s > 12:
                # Если лица не обнаружены, выводим количество секунд на экране
                cv2.putText(saturated_frame, f"Осталось: {countdown}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)
                countdown -= 1

                if countdown < 0:
                    # Когда счетчик достигнет 0, закрываем окно, камеру и счетчик
                    container.content.controls.pop()
                    container.update()
                    break
            else:
                countdown = 13

            # рисуем квадратик
            for (x, y, w, h) in faces:
                # ожидание отжимания вниз
                if y > 240 and s < 7:
                    s += 1
                elif y > 240:
                    c += 1
                # ожидание отжимания вверх
                if y < 80 and s < 13 and s > 6:
                    s += 1
                # посмотреть с
                elif y < 80 and c > 0:
                    c = 0
                    k += 1
                    container.content.controls.append(countergif)
            # рука для анимации
            countergif = ft.Container(
                ft.Image(
                    src=f"gym.gif",
                    width=100,
                    height=100),
                margin=ft.margin.only(left=950, top=500)
            )
            # текст отжимания
            counter= ft.Container(
                ft.Text(
                    'Отжимания:',
                    size=50,
                    color=ft.colors.YELLOW,
                    weight=ft.FontWeight.BOLD,
                    italic=True),
                margin=ft.margin.only(left=900, top=350)
            )
            # вывод количества отжиманий
            counter2 = ft.Container(
                ft.Text(
                    k,
                    size=100,
                    color=ft.colors.YELLOW,
                    weight=ft.FontWeight.BOLD,
                    italic=True),
                margin=ft.margin.only(left=950, top=400)
            )
            container.content.controls.append(counter)
            container.content.controls.append(counter2)
            container.update()
            container.content.controls.pop()
            container.content.controls.pop()
            # анимация
            if len(container.content.controls) > 14:
                t+=1
            if t > 2:
                t = 0
                container.content.controls.pop(14)
            # этап : начальное положение
            if s < 13:
                # начальная точка, конечная точка, цвет, толщина
                cv2.line(saturated_frame, (190, 420), (240, 420), (0, 0, 255), 2)
                cv2.line(saturated_frame, (420, 420), (470, 420), (0, 0, 255), 2)
                cv2.line(saturated_frame, (215, 395), (215, 445), (0, 0, 255), 2)
                cv2.line(saturated_frame, (445, 395), (445, 445), (0, 0, 255), 2)
                cv2.putText(saturated_frame, "waiting for the game to start...", (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)
            # обновление фрейма
            _, im_arr = cv2.imencode('.png', saturated_frame)
            im_b64 = base64.b64encode(im_arr)
            self.img.src_base64 = im_b64.decode("utf-8")
            self.update()

    def build(self):
        # вывод камеры во flet
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20)
        )
        return self.img


# открытие камеры по кнопке, обновление контейнера
def open_camera(e):
    camera = ft.Container(
        border_radius=ft.border_radius.all(20),
        content=ft.Column([
            flying_head(),
        ]),
        margin=ft.margin.only(left=250, top=250)
    )
    container.content.controls.append(camera)
    container.update()


# игра отжимания
def open_camera2(e):
    camera = ft.Container(
        border_radius=ft.border_radius.all(20),
        content=ft.Column([
            push_up(),
        ]),
        margin=ft.margin.only(left=250, top=250)
    )
    container.content.controls.append(camera)
    container.update()



# кнопка 1 игры
button = ft.Container(ft.ElevatedButton(
    'Flying Head',
    on_click=open_camera,
    width=200,
    height=50,
    color='#000000',
    bgcolor='#d4f211'
),
    margin=ft.margin.only(left=900, top=800)
)

# кнопка 2 игры
button2 = ft.Container(ft.ElevatedButton(
    'Счётчик отжиманий',
    on_click=open_camera2,
    width=200,
    height=50,
    color='#000000',
    bgcolor='#d4f211'
),
    margin=ft.margin.only(left=900, top=1000)
)

# Создание основного фона
main_bg = ft.Row(
    controls=[
        ft.Container(
            width=1080,
            height=1080,
            bgcolor='#3450a1',
            border_radius=35,
            margin=ft.margin.all(150)
        )
    ]
)
# Создание фона для информации
info_bg = ft.Row(
    controls=[
        ft.Container(
            width=650,
            height=1080,
            bgcolor='#5922b3',
            border_radius=35,
            margin=ft.margin.only(left=1300, top=150)
        )
    ]
)

# текст имя проекта
name_proj = ft.Container(
    ft.Text("Push up coach master", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=210)
)

# иконка мирэа
mirea = ft.Container(
    ft.Image(
        src=f"mirea.jfif",
        width=300,
        height=300),
    margin=ft.margin.only(left=1470, top=320)
)

# текст разработчики
developers = ft.Container(
    ft.Text("разработчики:", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=700)
)

antonov = ft.Container(
    ft.Text("antonov", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=750)
)

ishutin = ft.Container(
    ft.Text("ishutin", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=800)
)

kagarmanov = ft.Container(
    ft.Text("kagarmanov", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=850)
)

gurin = ft.Container(
    ft.Text("gurin", color='#ffff00', size=40),
    margin=ft.margin.only(left=1400, top=900)
)

# текстовое поля для игры 1
rule_game = ft.Container(
    ft.Text("Поднимайся и опускайся, чтобы не задеть предметы", color='#000000', size=20),
    margin=ft.margin.only(left=250, top=800)
)

# текстовое поля для игры 2
rule_game2 = ft.Container(
    ft.Text("Подсчёт обычных отжиманий. Смотреть вперед!", color='#000000', size=20),
    margin=ft.margin.only(left=250, top=1000)
)

# Задний фон который включает в себя все контейнеры
container = ft.Container(
    width=2120,
    height=1800,
    bgcolor='#041955',
    margin=ft.margin.all(-100),
    content=ft.Stack(
        controls=[
            main_bg,
            info_bg,
            name_proj,
            button,
            button2,
            mirea,
            developers,
            antonov,
            ishutin,
            kagarmanov,
            gurin,
            rule_game,
            rule_game2
        ]
    )
)


# вызов основного кода

def main(page: ft.Page):
    page.add(container)


ft.app(target=main)
