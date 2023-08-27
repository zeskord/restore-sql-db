import flet as ft
from taskparse import parse_task, parse_from_text
import core
import win32clipboard

def main(page):
    def btn_run(e):
        e.control.disabled = True
        e.control.update()
        taskdata = get_task_data_from_form()
        try:
            core.restoredb(taskdata)
            page.controls.append(ft.Text("Завершено!"))
        except Exception as exception:
            exception_text = str(exception)
            page.controls.append(ft.Text(exception_text))
        finally:
            e.control.disabled = False
            page.update()

    def fill_fields_from_dict(input_data):
        # заполняем поля
        # сервер
        textField_sqlserver.value = input_data["sqlserver"]
        textField_sqlserver.update()
        # база данных
        textField_database.value = input_data["database"]
        textField_database.update()
        # бэкап источник
        textField_backup_source_file.value = input_data["backup_source_file"]
        textField_backup_source_file.update()
        # сетевой путь к транзитной папке
        textField_server_external_dir.value = input_data["server_external_dir"]
        textField_server_external_dir.update()
        # локальный путь к транзитной папке
        textField_server_dir.value = input_data["server_dir"]
        textField_server_dir.update()


    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_files.value = (
            ", ".join(map(lambda f: f.path, e.files)) if e.files else "Отменено!"
        )
        selected_files.update()
        input_data = parse_task(selected_files.value)
        fill_fields_from_dict(input_data)

    def get_task_data_from_form():
        return {
            "sqlserver": textField_sqlserver.value,
            "database": textField_database.value,
            "backup_source_file": textField_backup_source_file.value,
            "server_external_dir": textField_server_external_dir.value,
            "server_dir": textField_server_dir.value,
        }

    page.title = "Восстановление базы данных"

    # Выбор файла
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.Text()
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Выбери файл с заданием",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                selected_files,
            ]
        )
    )
    page.overlay.append(pick_files_dialog)

    # Чтение из буфера обмена
    def paste_task(e):
        # get clipboard data
        win32clipboard.OpenClipboard()
        clipboard_text = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        try:
            data = parse_from_text(clipboard_text)
            fill_fields_from_dict(data)
        except:
            # Не хочу возиться с алертом.
            pass
    
    page.add(
        ft.ElevatedButton(
            "Прочитать из буфера обмена",
            icon=ft.icons.CONTENT_PASTE,
            on_click=paste_task,
        ),
    )

    # Просто вывод полей.
    textField_sqlserver = ft.TextField(label="SQL-сервер")
    textField_database = ft.TextField(label="База данных")
    page.add(ft.Row([textField_sqlserver, textField_database]))

    textField_backup_source_file = ft.TextField(label="Файл бэкапа - источник")
    page.add(textField_backup_source_file)

    textField_server_dir = ft.TextField(
        label="Транзитная папка сервера - локальный путь"
    )
    page.add(textField_server_dir)

    # Разделитель.
    page.add(ft.Divider())

    textField_server_external_dir = ft.TextField(
        label="Транзитная папка сервера - сетевой путь"
    )
    page.add(textField_server_external_dir)

    # Разделитель.
    page.add(ft.Divider())

    # Теперь необязательные данные касающиеся 1С.
    textField_server1c = ft.TextField(label="Сервер 1С")
    textField_base1c = ft.TextField(label="База 1С")
    textField_program = ft.TextField(label="Программа 1С (экзешник)")

    container_1c_column = ft.Column(
        controls=[
            ft.Text("Необязательные поля, нужны для запуска 1С с праметром"),
            ft.Row([textField_server1c, textField_base1c]),
            textField_program,
        ]
    )

    container_1c = ft.Container(content=container_1c_column, padding=10)

    page.add(container_1c)

    button_Run = ft.ElevatedButton("Выполнить!", on_click=btn_run)
    page.add(button_Run)

ft.app(target=main)
