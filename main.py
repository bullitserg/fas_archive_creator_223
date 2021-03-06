from queries import *
from config import *
from os import listdir, chdir, mkdir, remove
from os.path import normpath, isfile, join, split, splitext, getsize
from ets.ets_xml_worker import found_procedure_223_db
from ets.ets_mysql_lib import MysqlConnection as Mc, get_query_top
from ets.ets_excel_creator import Excel
from random import randint
from shutil import copyfile, make_archive, rmtree
from time import sleep
from itertools import count
import re
import argparse

PROGNAME = 'FAS archive creator 223'
DESCRIPTION = '''Скрипт для формирования архивов по процедурам 223\n
[x] 223zk\n
[x] 223zp\n
[x] 223ea1\n
[x] 223ea2\n
[x] 223ek\n
[x] 223smsp_ea (без сведений о ЦП)\n
[x] 223smsp_ek (без сведений о ЦП)\n
[x] 223smsp_zk (без сведений о ЦП)\n
[x] 223smsp_zp (без сведений о ЦП)'''
VERSION = '1.1'
AUTHOR = 'Belim S.'
RELEASE_DATE = '2018-12-11'

DATA_PROCESSED = 0

work_dir = normpath(work_dir)


# функция создания поддиректории
def create_dir(name):
    try:
        mkdir(name)
    except FileExistsError:
        pass


# функция приводит в порядок путь до файлов соответствии со словарем documentDirs
def found_location_dir(smsp, data, dir_column):
    # data - данные выборки из запроса
    # dirColumn - номер колонки в данных, которая содержит путь
    out_list = []
    for link in data:
        link = list(link)

        if smsp:
            document_d = document_dirs_smsp
        else:
            document_d = document_dirs

        for prefix in document_d.keys():
            changing = re.subn(prefix, document_d[prefix], link[dir_column])
            if changing[1] == 1:
                link[dir_column] = changing[0]
                out_list.append(link)
                break
        # если ни один из keys не совпал, значит локейшен нам не известен
        else:
            print('One of documents of %(procedure_number)s located in unknown location' % globals())
    return out_list


# функция для проверки корректности номера процедуры
def test_procedure_number(procedure_number):
    if re.fullmatch(r'([0-9]{11})', procedure_number):
        return True
    else:
        return False


# функция создания рандомного короткого имени для файла
def get_rand_name(file_link):
    f_link, f_file = split(file_link)
    f_name, f_exp = splitext(f_file)
    f_name_rand = str(randint(0, 9999)).rjust(4, '0') + '~' + f_exp
    file_link = join(f_link, f_name_rand)
    return file_link


def show_version():
    print(PROGNAME, VERSION, '\n', DESCRIPTION, '\nAuthor:', AUTHOR, '\nRelease date:', RELEASE_DATE)


def procedure_archiving(procedure_number):
    global DATA_PROCESSED

    # инициализация sql подключений
    db_info = found_procedure_223_db(procedure_number)
    if not db_info:
        print('Процедура %(procedure_number)s не найдена' % vars())
        return

    cn = Mc(connection=db_info['connection'])
    is_smsp = db_info['db'] in ['223smsp_ea', '223smsp_ek', '223smsp_zk', '223smsp_zp']

    print('Обработка %(procedure_number)s начата' % vars())
    print(db_info['name'])
    # проверяем, существует ли уже архив для данной процедуры
    archive_procedures_list = [archive[0:11] for archive in listdir(work_dir) if archive.endswith('.zip')
                               and isfile(join(work_dir, archive))]

    if procedure_number in archive_procedures_list:
        print('Архив %(procedure_number)s.zip уже существует' % vars())
        return 0

    # создаем директорию процедуры и делаем ее рабочей директорией
    chdir(work_dir)
    create_dir(procedure_number)
    chdir(procedure_number)
    work_procedures_dir = join(work_dir, procedure_number)

    # Здесь будем хранить основной массив данных
    all_data = []

    print('- Получение данных')
    # обрабатываем заявки
    chdir(work_procedures_dir)
    with cn.open():
        requests_data = cn.execute_query(get_requests_data_query % vars())

    requests_data = found_location_dir(is_smsp, requests_data, 5)

    # находим для каждого файла составляющие пути, куда будем класть данный файл в архив
    # собираем их в лист allData
    for data in requests_data:
        archive_location_dir_parts = [str(data[1]), requests_dir, str(data[2]), str(data[3])]
        # uri, links_list, name
        request_data = [data[5], archive_location_dir_parts, str(data[4])]
        all_data.append(request_data)

    # обрабатываем протоколы
    chdir(work_procedures_dir)
    with cn.open():
        protocols_data = cn.execute_query(get_protocols_data_query % vars())
    protocols_data = found_location_dir(is_smsp, protocols_data, 4)

    # находим для каждого файла составляющие пути, куда будем класть данный файл в архив
    # собираем их в лист allData
    for data in protocols_data:
        archive_location_dir_parts = [str(data[1]), protocols_dir, str(data[2])]
        # uri, links_list, name
        protocol_data = [data[4], archive_location_dir_parts, str(data[3])]
        all_data.append(protocol_data)

    # обрабатываем фичи
    chdir(work_procedures_dir)
    with cn.open():
        features_data = cn.execute_query(get_features_data_query % vars())
    features_data = found_location_dir(is_smsp, features_data, 5)

    # находим для каждого файла составляющие пути, куда будем класть данный файл в архив
    # собираем их в лист allData
    for data in features_data:
        archive_location_dir_parts = [str(data[1]), requests_dir, str(data[2]), features_dir, str(data[3])]
        # uri, links_list, name
        feature_data = [data[5], archive_location_dir_parts, str(data[4])]
        all_data.append(feature_data)

    # если установлен флаг organisations, то добавляем в архив сведения об организации
    if namespace.organisation:
        # обрабатываем сведения о файлах организации
        chdir(work_procedures_dir)
        with cn.open():
            organisation_data = cn.execute_query(get_organisation_data_query % vars())
        organisation_data = found_location_dir(is_smsp, organisation_data, 5)

        # находим для каждого файла составляющие пути, куда будем класть данный файл в архив
        # собираем их в лист allData
        for data in organisation_data:
            archive_location_dir_parts = [str(data[2]), requests_dir, str(data[3]), organisation_data_dir, str(data[1])]
            # uri, links_list, name
            organisation_data = [data[5], archive_location_dir_parts, str(data[4])]
            all_data.append(organisation_data)

    # переименование директорий в соответствии со словарем dirNamesDict
    # замена обычных и фигурных скобок из-за проблем с re
    for data in all_data:
        renamed_dirs = []
        for location in data[1]:
            if location in dir_names_dict.keys():
                location = dir_names_dict[location]
            renamed_dirs.append(location)
        data[1] = renamed_dirs
        data[2] = re.sub(r'(\(|\)|\[|\])', '_', data[2])

    # собираем excel файл с ценовыми предложениями (если они есть)
    if db_info['db'] not in ['223smsp_ea', '223smsp_ek', '223smsp_zk', '223smsp_zp']:
        with cn.open():
            offers_data = list(cn.execute_query(get_offers_data_query % vars()))
        if offers_data:
            offer_top = get_query_top(get_offers_data_query % vars())
            excel_file = Excel()
            excel_list = excel_file.create_list(sheet_name='Ценовые предложения')
            excel_list.set_numeral(6)
            excel_list.write_data_from_iter(offers_data, offer_top)
            excel_list.set_default_column_width(150)
            excel_file.save_file(save_dir=work_procedures_dir, file_name='Ценовые предложения участников ' + procedure_number)

    # вычленяем из allData листы с директориями для формирования пути
    archive_locations = [archiveLocationDirParts[1] for archiveLocationDirParts in all_data]

    # создаем все необходимые нам директории
    for location in archive_locations:
        chdir(work_procedures_dir)
        for directory in location:
            directory = str(directory)
            create_dir(directory)
            chdir(directory)

    # формируем путь и добавляем его в archiveLocationsFromAndTo вместе с путем источника
    archive_locations_from_and_to = []
    for archive_location_dir_parts in all_data:
        archive_location_dir = join(*([work_procedures_dir] +
                                      archive_location_dir_parts[1] +
                                      [archive_location_dir_parts[2]]))

        archive_locations_from_and_to.append([normpath(archive_location_dir_parts[0]),
                                              normpath(archive_location_dir)])

    print('- Копирование файлов')
    # копируем файлы по директориям
    chdir(work_procedures_dir)
    for from_location, to_location in archive_locations_from_and_to:
        # если возникла ошибка OSError: [Errno 36] File name too long
        try:
            copyfile(from_location, to_location)
        except OSError as exc:
            if exc.errno == 36:
                to_location = get_rand_name(to_location)
                copyfile(from_location, to_location)
            else:
                raise  # re-raise previously caught exception

    # архивируем директорию и удаляем ее
    print('- Создание архива')
    chdir(work_dir)
    archive = make_archive(procedure_number, 'zip', work_procedures_dir)

    print('- Удаление временных файлов')
    rmtree(work_procedures_dir)

    archive_byte_size = getsize(archive)
    archive_MB_size = round(archive_byte_size / 1024 / 1024, 2)

    DATA_PROCESSED += archive_byte_size

    print('Создан архив: %(archive)s' % vars())
    print('Размер архива: %(archive_MB_size)s МБ' % vars())
    print('Обработка %(procedure_number)s завершена' % vars())
    return archive


# обработчик параметров командной строки
def create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-s', '--sleep', action='store', default=sleep_time, type=int,
                        help="Set sleep time (seconds), default %s" % sleep_time)

    parser.add_argument('-l', '--list', action='store_true',
                        help="Generate listing of archives")

    parser.add_argument('-o', '--organisation', action='store_true',
                        help="Add organisation documents in archive")

    parser.add_argument('-r', '--remove', action='store_true',
                        help="Remove old archives")

    parser.add_argument('-p', '--procedure', type=str,
                        help="Set procedure number for archiving")

    parser.add_argument('-f', '--file', action='store_true',
                        help="Get procedure number from file %s" % procedure_file)

    parser.add_argument('-v', '--version', action='store_true',
                        help="Show version")

    return parser

# ОСНОВНОЙ КОД
if __name__ == '__main__':
    # парсим аргументы командной строки
    parser = create_parser()
    namespace = parser.parse_args()
    # устанавливаем время задержки
    sleep_time = namespace.sleep

    # вывод версии
    if namespace.version:
        show_version()
        exit(0)

    # вывод списка ранее созданных архивов
    elif namespace.list:
        archive_list = [archive for archive in listdir(work_dir) if archive.endswith('.zip')
                        and isfile(join(work_dir, archive))]

        archive_list_count = len(archive_list)

        if archive_list:
            print('Найдено %s ранее созданныx архивов:\n' % archive_list_count, output_str_separator.join(archive_list))
        else:
            print('Архивы отсутствуют')
        exit(0)

    # удаление старых архивов
    elif namespace.remove:
        print('Удаление старых архивов')
        archive_list = [join(work_dir, archive) for archive in listdir(work_dir)
                        if archive.endswith('.zip') and isfile(join(work_dir, archive))]
        archive_list_length = len(archive_list)
        for archive in archive_list:
            remove(archive)
        print('Удалено %(archive_list_length)s архивов' % vars())
        exit(0)

    # обработка процедуры из командной строки
    elif namespace.procedure:
        if test_procedure_number(namespace.procedure):
            procedure_number = namespace.procedure
            procedure_archiving(procedure_number)
            exit(0)
        else:
            print('Указан некорректный номер процедуры')
            exit(1)

    # обработка процедур из файла
    elif namespace.file:
        print('Начинаем обработку файла %(procedure_file)s\n' % vars())
        # получаем данные из файла
        with open(procedure_file, mode='r', encoding='utf8') as open_procedure_file:
            procedure_file_data = []
            line = open_procedure_file.readline()
            while line:
                procedure_file_data.append(line.strip())
                line = open_procedure_file.readline()
    # отбираем корректные и некорректные номера аукционов
        procedures_for_archiving = []
        failed_procedures_for_archiving = []
        for procedure_number in procedure_file_data:
            procedure_number = procedure_number.strip(' ')
            if test_procedure_number(procedure_number):
                procedures_for_archiving.append(procedure_number)
            else:
                failed_procedures_for_archiving.append(procedure_number)

        # если найдены некорректные
        if failed_procedures_for_archiving:
            failed_procedures_for_archiving_count = len(failed_procedures_for_archiving)
            print('Найдено %(failed_procedures_for_archiving_count)s проблемных процедур' % vars())
            failed_procedures_for_archiving_str = output_str_separator.join(failed_procedures_for_archiving)
            print('Проблемные номера процедур: %(failed_procedures_for_archiving_str)s' % vars())
        print('')
        # если найдены корректные
        if procedures_for_archiving:
            procedures_for_archiving_count = len(procedures_for_archiving)

            # создаем счетчик для отсчета процедур
            procedures_counter = count(start=1, step=1)

            print('Найдено %(procedures_for_archiving_count)s процедур для обработки' % vars())

            # архивируем все корректные
            for procedure_number in procedures_for_archiving:
                print('Обработка %s из %s' % (next(procedures_counter), procedures_for_archiving_count))
                procedure_archiving(procedure_number)
                # вывод объема всех обработанных архивов
                data_processed_MB_size = round(DATA_PROCESSED / 1024 / 1024, 2)
                print('Объем всех созданных архивов: %(data_processed_MB_size)s МБ\n' % vars())
                sleep(sleep_time)
        exit(0)

    else:
        print('')
        show_version()
        print('\nUse -h/--help for more information\n')
        exit(0)
