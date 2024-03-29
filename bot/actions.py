import time

from aiogram import types

from dispatcher import dp
from distributor.move import create_and_open_folder, create_folder_path, copy_file
from distributor.process import get_map
from distributor.read import get_file_names
from .consts import *


@dp.message_handler(commands=["start"])
async def welcome_message(message: types.Message) -> None:
    await message.bot.send_message(message.from_user.id, START_TEXT, disable_web_page_preview=True)


@dp.message_handler()
async def handle_message(message: types.Message) -> None:
    if not message.text.startswith(('https://disk.yandex.ru/', 'https://yadi.sk/')):
        await message.bot.send_message(message.from_user.id, 'Некорректная ссылка')
        return

    await message.bot.send_message(message.from_user.id, 'Ссылка принята. Начал обработку, это займет немного времени.')

    url = message.text.strip()
    try:
        files = await get_file_names(link=url)
    except FileNotFoundError as e:
        await message.bot.send_message(message.from_user.id, str(e))
        return
    except Exception:
        await message.bot.send_message(
            message.from_user.id,
            'Что-то пошло не так. Попробуйте еще раз или напишите @arseny_volodko.'
        )
        return

    ru_map, unknown = await get_map(files)
    cur_time = str(int(time.time()))
    folder_path = f'tickets/tickets-{cur_time}'

    try:
        new_url = await create_and_open_folder(folder_path)
    except Exception:
        await message.bot.send_message(message.from_user.id,
                                       'Что-то пошло не так. Попробуйте еще раз или напишите @arseny_volodko'
                                       )
        return

    await message.bot.send_message(message.from_user.id,
                                   f'Билеты будут появляться по мере их обработки здесь: {new_url}')

    cnt = 0
    total = len(files)

    if unknown:
        await message.bot.send_message(message.from_user.id,
                                       f'Не удалось определить принадлежность {len(unknown)} файлов:')

        unknown_files = '\n'.join(map(lambda x: url + '/' + x, unknown))

        await message.bot.send_message(message.from_user.id, unknown_files, disable_web_page_preview=True)

    info_msg = None

    for user_name, tickets in ru_map.items():
        name = ' '.join(map(lambda x: x.capitalize(), user_name.split()))
        try:
            await create_folder_path(f'tickets/tickets-{cur_time}/{name}')
        except Exception:
            await message.bot.send_message(message.from_user.id, f"Не удалось создать папку для {name}.")
            continue
        for ticket in tickets:
            cnt += 1
            try:
                await copy_file(url, ticket, f'tickets/tickets-{cur_time}/{name}')
            except Exception:
                await message.bot.send_message(
                    message.from_user.id,
                    f"Не удалось скопировать файлы для участника: {name.capitalize()}.")
            if not info_msg:
                info_msg = await message.bot.send_message(message.from_user.id,
                                                          'Идет обработка. Обработано {} из {} билетов.'.format(cnt,
                                                                                                                total))
            else:
                await message.bot.edit_message_text('Идет обработка. Обработано {} из {} билетов.'.format(cnt, total),
                                                    message.from_user.id,
                                                    info_msg.message_id)

    for file in unknown:
        try:
            await copy_file(url, file, f'tickets/tickets-{cur_time}')
        except Exception:
            pass

    await message.bot.send_message(message.from_user.id, 'Обработка завершена.')
