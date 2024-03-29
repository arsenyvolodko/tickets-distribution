from collections import defaultdict
from unidecode import unidecode
from transliterate import translit


async def translit_name(name: str):
    if await check_word_lang(name, 'ru'):
        return unidecode(name).replace("'", '')
    else:
        return await clear_whole_name(translit(name, 'ru', reversed=False))


async def check_word_only_letters(word: str):
    for i in word:
        if not i.isalpha():
            return False
    return True


async def check_word_lang(word: str, code: str):
    if code == 'ru':
        r = range(1072, 1105)
    else:
        r = range(97, 123)
    if not word:
        return False
    for i in word:
        if not (ord(i) in r or i.isspace()):
            return False
    return True


async def replace_symbols(text, symbols: list, new_symbols: list):
    for ind, sym in enumerate(symbols):
        text = text.replace(sym, new_symbols[ind])
    return text


async def get_passenger_name(file_name: str):
    file_name = file_name.lower()
    file_name = await replace_symbols(file_name, ['_', '-', 'й'], [' ', ' ', 'й'])
    splited_file_name = file_name.split()
    list_name = []
    for word in splited_file_name:
        if len(list_name) == 2:
            break
        if await check_word_only_letters(word) and len(word) > 2:
            list_name.append(word)
    if len(list_name) == 2:
        return " ".join(list_name)
    return None


async def clear_name(name: str):
    name = name.replace('иу', 'ю')
    name = name.replace('кх', 'х')
    name = name.replace('шч', 'щ')
    flag = False
    if name[-3:] == 'ииа':
        name = name[:-3] + 'ия'
        flag = True
    if 'иа' in name:
        if name[-3:] == 'аиа':
            name = name[:-3] + 'ая'
        elif name[-2:] == 'иа':
            name = name[:-2] + 'ья'
        name = name.replace('иа', 'я')
    new_name = None
    if name[-2:] == 'ия' and not flag:
        new_name = name[:-2] + 'ья'
    elif name[-2:] == 'иа':
        new_name = name[:-2] + 'ья'
    elif name[-2:] == 'ии':
        new_name = name[:-2] + 'ий'
    elif name[-2:] == 'еи':
        new_name = name[:-2] + 'ей'
    if new_name:
        return new_name
    return name


async def clear_whole_name(name: str):
    splitted_name = name.split()
    return " ".join([await clear_name(word) for word in splitted_name])


async def get_map(files: list[str]):
    ru_map: dict[str, list[str]] = defaultdict(list)
    en_map: dict[str, list[str]] = defaultdict(list)
    unknown = []
    for file in files:
        cur_name = await get_passenger_name(file)
        if await check_word_lang(cur_name, 'ru'):
            ru_map[cur_name].append(file)
        elif await check_word_lang(cur_name, 'en'):
            en_map[cur_name].append(file)
        else:
            unknown.append(file)
    to_delete = []
    for name in en_map:
        if (ru_name := await translit_name(name)) in ru_map:
            ru_map[ru_name].extend(en_map[name])
            to_delete.append(name)
    for name in to_delete:
        del en_map[name]
    to_delete.clear()
    for name in ru_map:
        if (en_name := await translit_name(name)) in en_map:
            ru_map[name].extend(en_map[en_name])
            to_delete.append(en_name)
    for name in to_delete:
        del en_map[name]
    to_delete.clear()
    for name in en_map:
        ru_map[await translit_name(name)].extend(en_map[name])
    return ru_map, unknown
