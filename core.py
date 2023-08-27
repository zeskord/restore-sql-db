from logging import exception
import pyodbc
import os
import os.path

def restoredb(taskdata):
    sqlserver = taskdata["sqlserver"]
    database = taskdata["database"]
    backup_source_file = taskdata["backup_source_file"]
    server_external_dir = taskdata["server_external_dir"]
    server_dir = taskdata["server_dir"]

    backup_source_file_basename = os.path.basename(backup_source_file)
    backup_filename = os.path.join(server_dir, backup_source_file_basename)

    if os.path.exists(backup_filename) == False:
        print("Приступаем к копированию файла бэкапа.")
        os.system(f'copy "{backup_source_file}" "{backup_filename}"')

    print(backup_filename)
    assert os.path.exists(backup_filename) == True, f'Не удалось скопировать файл бэкапа из сетевой папки на диск сервера. {backup_filename}'

    # указываем драйвер
    driver = 'DRIVER={SQL Server}'
    # SQL сервер
    sqlserver = f'SERVER={sqlserver}'
    # указываем порт
    port = 'PORT=1433'

    db = f'DATABASE={database}'

    # ac = "autocommit=True"
    sspi = "Integrated Security=SSPI;"

    # соберем строку подключения к серверу
    conn_str = ';'.join([driver, sqlserver, port, db, sspi])

    # подключаемся к базе
    base_conn = pyodbc.connect(conn_str)
    base_conn.autocommit = True

    cursor = base_conn.cursor()

    data_logical_name = ""
    log_logical_name = ""
    cursor.execute("select name, type from sys.database_files")
    logical_name_files = cursor.fetchall()
    logical_name_files_list = []
    for logical_name in logical_name_files:
        if logical_name[1] == 0:
            data_logical_name = logical_name[0]
        elif logical_name[1] == 1: 
            log_logical_name = logical_name[0]   

    assert data_logical_name != "", "Не удалось получить логическое имя файла данных"
    assert log_logical_name != "", "Не удалось получить логическое имя файла лога"
        
    data_file_name = "";
    log_file_name = "";
    cursor.execute(f"select physical_name from [{database}].sys.database_files")
    real_file_names = cursor.fetchall()
    for file_name in real_file_names:
        if file_name[0].lower().endswith(".mdf"):
            data_file_name = file_name[0]
        elif file_name[0].lower().endswith(".ldf"):
            log_file_name = file_name[0]

    assert data_file_name != "", "Не удалось получить имя файла данных"
    assert log_file_name != "", "Не удалось получить имя файла лога"

    cursor.execute(f"ALTER DATABASE [{database}] SET OFFLINE WITH ROLLBACK IMMEDIATE")
    cursor.execute(f"RESTORE FILELISTONLY FROM DISK=N'{str(backup_filename)}'")
    cursor.execute(f"RESTORE DATABASE [{database}] FROM DISK=N'{str(backup_filename)}' WITH REPLACE," 
        f" MOVE '{data_logical_name}' TO '{data_file_name}', MOVE '{log_logical_name}' TO '{log_file_name}'")

    while cursor.nextset():
        pass
    cursor.close()
