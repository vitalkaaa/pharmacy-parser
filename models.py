from mongoengine import *


class NormativeDocument(EmbeddedDocument):
    number = StringField()  # "Номер НД"
    date = DateField()  # "Год"
    change_number = StringField()  # "№ изм"
    name = StringField()  # "Наименование"


class ProductionStage(EmbeddedDocument):
    stage = StringField()  # "Стадия производства"
    producer = StringField()  # "Производитель"
    address = StringField()  # "Адрес производителя"
    country = StringField()  # "Страна"


class ReleaseForm(EmbeddedDocument):
    dosage_form = StringField()  # "Лекарственная форма"
    dosage = StringField()  # "Дозировка"
    expiration_date = StringField()  # "Срок годности"
    storage_conditions = StringField()  # "Условия хранения"
    packing = ListField(StringField())  # "Упаковки"


class ATCClassification(EmbeddedDocument):
    atc = StringField()  # "АТХ"
    code = StringField()  # "Код АТХ"


class MNN(Document):
    name = StringField()
    name_ru = StringField()


class Substance(Document):
    guid = StringField()  # site GUID
    mnn = ReferenceField(MNN)  # "Международное непатентованное наим. или группировочное наименование" en language
    mnn_orig = StringField()  # "Международное непатентованное наим. или группировочное наименование" orig language
    name = StringField()  # "Наименование фармацевтической субстанции" en language
    name_orig = StringField()  # "Наименование фармацевтической субстанции" orig language
    producer = StringField()  # "Производитель"
    reg_id = StringField(primary_key=True)  # "Номер реестровой записи"
    reg_start_date = DateField()  # "Дата включения в реестр"
    reg_end_date = DateField()  # "Дата исключения из реестра"
    decision_date = DateField()  # "Дата решения"
    status = StringField()  # "Статус"
    release_forms = EmbeddedDocumentListField(ReleaseForm)  # "Форма выпуска"
    production_stages = EmbeddedDocumentListField(ProductionStage)  # "Сведения о стадиях производства"
    normative_documents = EmbeddedDocumentListField(NormativeDocument)  # "Нормативная документация"


class Medicine(Document):
    guid = StringField()  # site GUID
    mnn = ListField(ReferenceField(MNN))  # Список мнн ( А+B -> [A, B] ) en language
    mnn_orig = ListField(StringField)  # Список мнн ( А+B -> [A, B] ) orig language
    trade_name = StringField()  # "Торговое наименование"
    reg_owner = StringField()  # "Наименование держателя или владельца рег. удостоверения лекарственного препарата"
    reg_country = StringField()  # "Страна держателя или владельца рег. удостоверения лекарственного препарата"
    reg_id = StringField(primary_key=True)  # "Номер реестровой записи"
    reg_start_date = DateField()  # "Дата включения в реестр"
    reg_end_date = DateField()  # "Дата исключения из реестра"
    reg_renewal_date = DateField()  # "Дата переоформления РУ"
    decision_date = DateField()  # "Дата решения"
    status = StringField()  # "Статус"
    pharmacotherapeutic_group = StringField()  # "Фармако-терапевтическая группа"
    normative_documents = EmbeddedDocumentListField(NormativeDocument)  # "Нормативная документация"
    release_forms = EmbeddedDocumentListField(ReleaseForm)  # "Форма выпуска"
    release_forms_collapsed = StringField()  # "Форма выпуска с главной"
    production_stages = EmbeddedDocumentListField(ProductionStage)  # "Сведения о стадиях производства"
    substances = ListField(Substance)  # "Фармацевтическая субстанция"



