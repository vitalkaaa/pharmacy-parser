from datetime import datetime

import requests
from lxml import html

from models import *

MEDICINE_MAIN_PAGE_URL = 'http://grls.rosminzdrav.ru/GRLS.aspx?RegNumber=&MnnR=%s&lf=&TradeNmR=&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs=0&isND=-1&regtype=1&pageSize=10&order=RegDate&orderType=desc&pageNum=%s'
MEDICINE_EXT_PAGE_URL = 'http://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=%s&t='

SUBSTANCE_MAIN_PAGE_URL = 'http://grls.rosminzdrav.ru/GRLS.aspx?RegNumber=&MnnR=%s&lf=&TradeNmR=&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs=1&isND=0&order=RegDate&orderType=desc&RegType=1&pageSize=10&pageNum=%s'
SUBSTANCE_EXT_PAGE_URL = 'http://grls.rosminzdrav.ru/Grls_viewFS_v2.aspx?routingGuid=%s&t='


def parse_medicine_main_page(entry_html_object, medicine: Medicine):
    entry_as_list = entry_html_object.xpath('./td/text()')

    medicine.guid = entry_html_object.xpath('@onclick')[0][5:-5]
    medicine.trade_name = entry_as_list[1]
    medicine.mnn = MNN.objects(name_ru__in=[i.upper() for i in entry_as_list[2].split('+')])
    medicine.mnn_orig = entry_as_list[2]
    medicine.release_forms_collapsed = entry_as_list[3]
    medicine.reg_owner = entry_as_list[4]
    medicine.reg_country = entry_as_list[5]
    medicine.reg_id = entry_as_list[6]
    medicine.reg_start_date = entry_as_list[7]
    medicine.reg_start_date = datetime.strptime(entry_as_list[7], '%d.%m.%Y')
    medicine.reg_end_date = datetime.strptime(entry_as_list[8], '%d.%m.%Y') if entry_as_list[6] == ' ' else None
    medicine.reg_renewal_date = datetime.strptime(entry_as_list[9], '%d.%m.%Y') if entry_as_list[6] == ' ' else None
    medicine.status = entry_as_list[10]
    medicine.decision_date = datetime.strptime(entry_as_list[11], '%d.%m.%Y') if entry_as_list[6] == ' ' else None


def parse_medicine_ext_page(html_object, medicine: Medicine, mnn: MNN):
    topics = html_object.xpath('//tr[@class="ter1"]')

    # Формы выпуска
    try:
        item = topics[4].xpath('.//tr[@class="hi_sys"]')
        for i, el in enumerate(item[::2]):
            html_o1 = item[2*i]
            html_o2 = item[2*i + 1]

            release_form = ReleaseForm()
            release_form.dosage_form = html_o1.xpath('./td')[0].text_content()
            release_form.dosage = html_o1.xpath('./td')[1].text_content()
            release_form.expiration_date = html_o1.xpath('./td')[2].text_content()
            release_form.storage_conditions = html_o1.xpath('./td')[3].text_content()
            release_form.packing = [p.text_content() for p in html_o2.xpath('.//li')]
            medicine.release_forms = list()
            medicine.release_forms.append(release_form)
    except IndexError:
        print('ERROR: форма выпуска')

    # Сведения о стадиях производства
    try:
        item = topics[5].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            production_stage = ProductionStage()
            production_stage.stage = html_o.xpath('./td')[1].text_content()
            production_stage.producer = html_o.xpath('./td')[2].text_content()
            production_stage.address = html_o.xpath('./td')[3].text_content()
            production_stage.country = html_o.xpath('./td')[4].text_content()
            medicine.production_stages = list()
            medicine.production_stages.append(production_stage)
    except IndexError:
        print('ERROR: Сведения о стадиях производства')

    # Нормативная документация
    try:
        item = topics[7].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            normative_document = NormativeDocument()
            normative_document.number = html_o.xpath('./td')[1].text_content()
            normative_document.date = datetime.strptime(html_o.xpath('./td')[2].text_content(), '%Y')
            normative_document.change_number = html_o.xpath('./td')[3].text_content()
            normative_document.name = html_o.xpath('./td')[4].text_content()
            medicine.normative_documents = list()
            medicine.normative_documents.append(normative_document)
    except IndexError:
        print('ERROR: Нормативная документация')

    # Фармако-терапевтическая группа
    try:
        medicine.pharmacotherapeutic_group = topics[8].xpath('.//tr[@class="hi_sys"]/td')[0].text_content()
    except IndexError:
        print('ERROR: Фармако-терапевтическая группа')

    # TODO: Анатомо-терапевтическая химическая классификация
    try:
        item = topics[9].xpath('.//tr[@class="hi_sys"]/td')
        atc = ATCClassification()
        atc.atc = item[1].text_content()
        atc.code = item[0].text_content()
        medicine.atc_classification = atc
    except IndexError:
        print('ERROR: Анатомо-терапевтическая химическая классификация')

    # TODO: Фармацевтическая субстанция
    try:
        item = topics[10].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            substance = MedicineSubstanceEntry()
            substance.mnn = mnn
            substance.name_orig = html_o.xpath('./td')[1].text_content()
            producer = Substance.objects(production_stages__match={'producer': html_o.xpath('./td')[2].text_content()}).first()
            if producer:
                substance.producer = producer
            substance.address = html_o.xpath('./td')[3].text_content()
            substance.expiration_date = html_o.xpath('./td')[4].text_content()
            substance.storage_conditions = html_o.xpath('./td')[5].text_content()
            substance.number = html_o.xpath('./td')[6].text_content()
            substance.drug_status = html_o.xpath('./td')[7].text_content()
            medicine.substances = list()
            medicine.substances.append(substance)
    except IndexError:
        print('ERROR: Фармацевтическая субстанция')


def parse_substance_main_page(entry_html_object, substance: Substance):
    entry_as_list = entry_html_object.xpath('./td/text()')
    for e in entry_as_list:
        e = e.replace(u'\xa0', '')

    substance.guid = entry_html_object.xpath('@onclick')[0][5:-5]
    substance.name_orig = entry_as_list[1]
    substance.producer = entry_as_list[3]
    substance.reg_id = entry_as_list[4]
    substance.reg_start_date = datetime.strptime(entry_as_list[5], '%d.%m.%Y')
    substance.reg_end_date = datetime.strptime(entry_as_list[6], '%d.%m.%Y') if entry_as_list[6] == ' ' else None
    substance.status = entry_as_list[7]
    substance.decision_date = datetime.strptime(entry_as_list[8], '%d.%m.%Y') if entry_as_list[8] == ' ' else None


def parse_substance_ext_page(html_object, substance: Substance):
    topics = html_object.xpath('//tr[@class="ter1"]')

    # Формы выпуска
    try:
        item = topics[5].xpath('.//tr[@class="hi_sys"]')
        for i, el in enumerate(item[::2]):
            html_o1 = item[2*i]
            html_o2 = item[2*i + 1]

            release_form = ReleaseForm()
            release_form.dosage_form = html_o1.xpath('./td')[0].text_content()
            release_form.dosage = html_o1.xpath('./td')[1].text_content()
            release_form.expiration_date = html_o1.xpath('./td')[2].text_content()
            release_form.storage_conditions = html_o1.xpath('./td')[3].text_content()
            release_form.packing = [p.text_content() for p in html_o2.xpath('.//li')]
            substance.release_forms = list()
            substance.release_forms.append(release_form)
    except IndexError:
        print('ERROR: форма выпуска')

    # Сведения о стадиях производства
    try:
        item = topics[6].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            production_stage = ProductionStage()
            production_stage.stage = html_o.xpath('./td')[1].text_content()
            production_stage.producer = html_o.xpath('./td')[2].text_content()
            production_stage.address = html_o.xpath('./td')[3].text_content()
            production_stage.country = html_o.xpath('./td')[4].text_content()
            substance.production_stages = list()
            substance.production_stages.append(production_stage)
    except IndexError:
        print('ERROR: Сведения о стадиях производства')

    # Нормативная документация
    try:
        item = topics[7].xpath('.//tr[@class="hi_sys"]')
        for html_o in item:
            normative_document = NormativeDocument()
            normative_document.number = html_o.xpath('./td')[1].text_content()
            if html_o.xpath('./td')[2].text_content() != u'\xa0':
                normative_document.date = datetime.strptime(html_o.xpath('./td')[2].text_content(), '%Y')
            normative_document.change_number = html_o.xpath('./td')[3].text_content()
            normative_document.name = html_o.xpath('./td')[4].text_content()
            substance.normative_documents = list()
            substance.normative_documents.append(normative_document)
    except IndexError:
        print('ERROR: Нормативная документация')


def parse_medicine(mnn):
    page_count = 1
    for page_num in range(1, 100):
        print(f'{mnn.name_ru} {MEDICINE_MAIN_PAGE_URL % (mnn.name_ru, page_num)}')
        response = requests.get(MEDICINE_MAIN_PAGE_URL % (mnn.name_ru, page_num))
        html_main = html.fromstring(response.text)

        for attempt in range(5):
            try:
                if page_num == 1:
                    page_count = int(html_main.xpath('//span[@id="ctl00_plate_lrecn"]/text()')[0].split(': ')[-1]) // 10 + 1

                for entry_html_object in html_main.xpath('//tr[@class="hi_sys poi"]'):
                    medicine = Medicine()
                    parse_medicine_main_page(entry_html_object, medicine)

                    response = requests.get(MEDICINE_EXT_PAGE_URL % medicine.guid)
                    html_ext = html.fromstring(response.text)

                    parse_medicine_ext_page(html_ext, medicine, mnn)
                    medicine.save()

            except IndexError:
                print(f'Attempt {attempt + 1} error. Retrying...')
            else:
                break

        if page_num == page_count:
            return


def parse_substance(mnn):
    page_count = 1
    for page_num in range(1, 100):
        print(f'Substance {mnn.name_ru}')
        response = requests.get(SUBSTANCE_MAIN_PAGE_URL % (mnn.name_ru, page_num))
        html_main = html.fromstring(response.text)

        for attempt in range(5):
            try:
                if page_num == 1:
                    page_count = int(html_main.xpath('//span[@id="ctl00_plate_lrecn"]/text()')[0].split(': ')[-1]) // 10 + 1

                for entry_html_object in html_main.xpath('//tr[@class="hi_sys poi"]'):
                    substance = Substance(mnn=mnn)
                    parse_substance_main_page(entry_html_object, substance)

                    response = requests.get(SUBSTANCE_EXT_PAGE_URL % substance.guid)
                    html_ext = html.fromstring(response.text)

                    parse_substance_ext_page(html_ext, substance)
                    substance.save()

            except IndexError:
                print(f'Attempt {attempt + 1} error. Retrying...')
            else:
                break

        if page_num == page_count:
            return
