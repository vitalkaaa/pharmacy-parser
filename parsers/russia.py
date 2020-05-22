import requests
from lxml import html

MEDICINE_MAIN_PAGE_URL = 'http://grls.rosminzdrav.ru/GRLS.aspx?RegNumber=&MnnR=%s&lf=&TradeNmR=&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs=0&isND=-1&regtype=1&pageSize=10&order=RegDate&orderType=desc&pageNum=%s'
MEDICINE_EXT_PAGE_URL = 'http://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=%s&t='

SUBSTANCE_MAIN_PAGE_URL = 'http://grls.rosminzdrav.ru/GRLS.aspx?RegNumber=&MnnR=%s&lf=&TradeNmR=&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs=1&isND=0&order=RegDate&orderType=desc&RegType=1&pageSize=10&pageNum=%s'
SUBSTANCE_EXT_PAGE_URL = 'http://grls.rosminzdrav.ru/Grls_viewFS_v2.aspx?routingGuid=%s&t='


def parse_medicine_main_page(entry_html_object):
    entry_as_list = entry_html_object.xpath('./td/text()')
    guid = entry_html_object.xpath('@onclick')[0][5:-5]
    return {
        'guid': guid,
        'Торговое наименование': entry_as_list[1],
        'Международное непатентованное наименование или группировочное (химическое) наименование': entry_as_list[2],
        'Форма выпуска': entry_as_list[3],
        'Наименование держателя или владельца регистрационного удостоверения лекарственного препарата': entry_as_list[4],
        'Страна держателя или владельца регистрационного удостоверения лекарственного препарата': entry_as_list[5],
        'Регистрационный номер': entry_as_list[6],
        'Дата государственной регистрации': entry_as_list[7],
        'Дата окончания действ. рег. уд.': entry_as_list[8],
        'Дата переоформления РУ': entry_as_list[9],
        'Состояние': entry_as_list[10],
        'Дата решения': entry_as_list[11],
    }


def parse_medicine_ext_page(html_object):
    topics = html_object.xpath('//tr[@class="ter1"]')
    entry = {
        'Форма выпуска': [],
        'Сведения о стадиях производства': [],
        'Нормативная документация': [],
        'Фармацевтическая субстанция': []
    }

    # Формы выпуска
    try:
        item = topics[4].xpath('.//tr[@class="hi_sys"]')
        for i, el in enumerate(item[::2]):
            html_o1 = item[2*i]
            html_o2 = item[2*i + 1]

            entry['Форма выпуска'].append({
                'Лекарственная форма': html_o1.xpath('./td')[0].text_content(),
                'Дозировка': html_o1.xpath('./td')[1].text_content(),
                'Срок годности': html_o1.xpath('./td')[2].text_content(),
                'Условия хранения': html_o1.xpath('./td')[3].text_content(),
                'Упавковки': [p.text_content() for p in html_o2.xpath('.//li')]
            })
    except IndexError:
        print('ERROR: форма выпуска')

    # Сведения о стадиях производства
    try:
        item = topics[5].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            entry['Сведения о стадиях производства'].append({
                'Стадия производства': html_o.xpath('./td')[1].text_content(),
                'Производитель': html_o.xpath('./td')[2].text_content(),
                'Адрес производителя': html_o.xpath('./td')[3].text_content(),
                'Страна': html_o.xpath('./td')[4].text_content(),
            })
    except IndexError:
        print('ERROR: Сведения о стадиях производства')

    # Нормативная документация
    try:
        item = topics[7].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            entry['Нормативная документация'].append({
                'Номер НД': html_o.xpath('./td')[1].text_content(),
                'Год': html_o.xpath('./td')[2].text_content(),
                '№ изм': html_o.xpath('./td')[3].text_content(),
                'Наименование': html_o.xpath('./td')[4].text_content(),
            })
    except IndexError:
        print('ERROR: Нормативная документация')

    # Фармако-терапевтическая группа
    try:
        item = topics[8].xpath('.//tr[@class="hi_sys"]/td')
        entry['Нормативная документация'] = item[0].text_content()
    except IndexError:
        print('ERROR: Фармако-терапевтическая группа')

    # Анатомо-терапевтическая химическая классификация
    try:
        item = topics[9].xpath('.//tr[@class="hi_sys"]/td')
        entry['Анатомо-терапевтическая химическая классификация'] = {
            'Код АТХ': item[0].text_content(),
            'АТХ': item[1].text_content(),
        }
    except IndexError:
        print('ERROR: Анатомо-терапевтическая химическая классификация')

    # Фармацевтическая субстанция
    try:
        item = topics[10].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            entry['Фармацевтическая субстанция'].append({
                'Международное непатентованное/группировочное/химическое наименование': html_o.xpath('./td')[0].text_content(),
                'Торговое наименование': html_o.xpath('./td')[1].text_content(),
                'Производитель': html_o.xpath('./td')[2].text_content(),
                'Адрес': html_o.xpath('./td')[3].text_content(),
                'Срок годности': html_o.xpath('./td')[4].text_content(),
                'Условия хранения': html_o.xpath('./td')[5].text_content(),
                'Фармакоп. статья / Номер НД': html_o.xpath('./td')[6].text_content(),
                'Нарк. прекурсор': html_o.xpath('./td')[7].text_content(),
            })
    except IndexError:
        print('ERROR: Фармацевтическая субстанция')

    return entry


def parse_substance_main_page(entry_html_object):
    entry_as_list = entry_html_object.xpath('./td/text()')
    guid = entry_html_object.xpath('@onclick')[0][5:-5]
    return {
        'guid': guid,
        'Наименование фармацевтической субстанции': entry_as_list[1],
        'Международное непатентованное наименование или группировочное (химическое) наименование': entry_as_list[2],
        'Производитель': entry_as_list[3],
        'Номер реестровой записи': entry_as_list[4],
        'Дата включения в реестр': entry_as_list[5],
        'Дата исключения из реестра': entry_as_list[6],
        'Состояние': entry_as_list[7],
        'Дата решения': entry_as_list[8],
    }


def parse_substance_ext_page(html_object):
    topics = html_object.xpath('//tr[@class="ter1"]')
    entry = {
        'Форма выпуска': [],
        'Сведения о стадиях производства': [],
        'Нормативная документация': []
    }

    # Формы выпуска
    try:
        item = topics[5].xpath('.//tr[@class="hi_sys"]')
        for i, el in enumerate(item[::2]):
            html_o1 = item[2*i]
            html_o2 = item[2*i + 1]

            entry['Форма выпуска'].append({
                'Лекарственная форма': html_o1.xpath('./td')[0].text_content(),
                'Дозировка': html_o1.xpath('./td')[1].text_content(),
                'Срок годности': html_o1.xpath('./td')[2].text_content(),
                'Условия хранения': html_o1.xpath('./td')[3].text_content(),
                'Упавковки': [p.text_content() for p in html_o2.xpath('.//li')]
            })
    except IndexError:
        print('ERROR: форма выпуска')

    # Сведения о стадиях производства
    try:
        item = topics[6].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            entry['Сведения о стадиях производства'].append({
                'Стадия производства': html_o.xpath('./td')[1].text_content(),
                'Производитель': html_o.xpath('./td')[2].text_content(),
                'Адрес производителя': html_o.xpath('./td')[3].text_content(),
                'Страна': html_o.xpath('./td')[4].text_content(),
            })
    except IndexError:
        print('ERROR: Сведения о стадиях производства')

    # Нормативная документация
    try:
        item = topics[7].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            entry['Нормативная документация'].append({
                'Номер НД': html_o.xpath('./td')[1].text_content(),
                'Год': html_o.xpath('./td')[2].text_content(),
                '№ изм': html_o.xpath('./td')[3].text_content(),
                'Наименование': html_o.xpath('./td')[4].text_content(),
            })
    except IndexError:
        print('ERROR: Нормативная документация')

    return entry


def parse_medicine(mnn):
    medicine_list = list()
    page_count = 1
    for page_num in range(1, 100):
        print(f'{mnn} page {page_num} {MEDICINE_MAIN_PAGE_URL % (mnn, page_num)}')
        response = requests.get(MEDICINE_MAIN_PAGE_URL % (mnn, page_num))
        root = html.fromstring(response.text)

        for attempt in range(3):
            try:
                if page_num == 1:
                    page_count = int(root.xpath('//span[@id="ctl00_plate_lrecn"]/text()')[0].split(': ')[-1]) // 10 + 1

                for entry_html_object in root.xpath('//tr[@class="hi_sys poi"]'):
                    main_entry_object = parse_medicine_main_page(entry_html_object)

                    response = requests.get(MEDICINE_EXT_PAGE_URL % main_entry_object['guid'])
                    root = html.fromstring(response.text)
                    print(main_entry_object)
                    extended_entry_object = parse_medicine_ext_page(root)

                    medicine_list.append(dict(main_entry_object, **extended_entry_object))

            except IndexError:
                print(f'Attempt {attempt + 1} error. Retrying...')
            else:
                break

        if page_num == page_count:
            return medicine_list


def parse_substance(mnn):
    substance_list = list()
    page_count = 1
    for page_num in range(1, 100):
        print(f'{mnn} page {page_num} {SUBSTANCE_MAIN_PAGE_URL % (mnn, page_num)}')
        response = requests.get(SUBSTANCE_MAIN_PAGE_URL % (mnn, page_num))
        root = html.fromstring(response.text)

        for attempt in range(3):
            try:
                if page_num == 1:
                    page_count = int(root.xpath('//span[@id="ctl00_plate_lrecn"]/text()')[0].split(': ')[-1]) // 10 + 1

                for entry_html_object in root.xpath('//tr[@class="hi_sys poi"]'):
                    main_entry_object = parse_substance_main_page(entry_html_object)

                    response = requests.get(SUBSTANCE_EXT_PAGE_URL % main_entry_object['guid'])
                    root = html.fromstring(response.text)
                    print(main_entry_object)
                    extended_entry_object = parse_substance_ext_page(root)

                    substance_list.append(dict(main_entry_object, **extended_entry_object))
            except IndexError:
                print(f'Attempt {attempt + 1} error. Retrying...')
            else:
                break

        if page_num == page_count:
            return substance_list
