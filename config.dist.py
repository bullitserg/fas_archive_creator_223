work_dir = 'C:/Users/belim/PycharmProjects/Архивы для ФАС 223/tmp'
procedure_file = 'C:/Users/belim/PycharmProjects/Архивы для ФАС 223/tmp/procedures.list'


requests_dir = 'Документы заявок'
protocols_dir = 'Документы протоколов'
features_dir = 'Документы преференций'
organisation_data_dir = 'Аккредитационные документы'

sleep_time = 3
output_str_separator = ','

dir_names_dict = {
    'request_additionaldocument': 'Иные документы',
    'request_agreementadditionaldocument': 'Согласие - Дополнительные документы',
    'request_confirmitydocumentationdocument': 'Документы, подтверждающие соответствие участника',
    'protocol_fz223-ea2-requestProtocol': 'Протокол первых частей',
    'protocol_finalRequestProtocol': 'Протокол вторых частей',
    'features_forSmallOrMiddle': 'СМП',
    'features_nationalTreatment': 'Условия, запреты, ограничения допуска товаров иностранного происхождения',
    'features_subcontractorsRequirement': 'Участникам, привлекающим СОНКО в качестве соисполнителей',
    'organization_document_1':	'Другие документы',
    'organization_document_3':	'Регистрационные документы',
    'organization_document_5':	'Документы, подтверждающие изменения данных',
    'organization_document_7':	'Копия документа, удостоверяющего личность',
    'organization_document_9':	'Копия выписки из ЕГРИП',
    'organization_document_11':	'Копия выписки из ЕГРЮЛ',
    'organization_document_13':	'Копии учредительных документов (Устав)',
    'organization_document_15':	'Заверенный перевод на русский язык документов о государственной регистрации',
    'organization_document_17':	'Копии документов, подтверждающих полномочия лица на получение аккредитации',
    'organization_document_19':	'Копии документов, подтверждающих полномочия руководителя',
    'organization_document_21':	'Копия решения об одобрении'
}


document_dirs = {'s223:///': '/upl/srv/www/sectionks-archive/data/upload/',
                 'fz94:///': '/upl/srv/www/auction-archive/public/upload/',
                 'fz94_1:///': '/upl/srv/www/auction-archive/public/upload1/',
                 'fz94_2:///': '/upl/srv/www/auction-archive-upload2/public/upload2/',
                 'fz94_5:///': '/upl/srv/www/auction-archive-upload5/public/upload5/',
                 'fz94_7:///': '/upl/srv/www/auction/public/upload7/',
                 'local:///': '/upl/srv/www/223/',
                 'local3:///': '/upl/srv/www/sectionks-archive/data/upload3/',
                 'local6:///': '/upl/srv/www/sectionks/data/upload6/'
                 }


document_dirs_smsp = {'s223:///': '/upl/srv/www/sectionks-archive/data/upload/',
                      'fz94:///': '/upl/srv/www/auction-archive/public/upload/',
                      'fz94_1:///': '/upl/srv/www/auction-archive/public/upload1/',
                      'fz94_2:///': '/upl/srv/www/auction-archive-upload2/public/upload2/',
                      'fz94_5:///': '/upl/srv/www/auction-archive-upload5/public/upload5/',
                      'fz94_7:///': '/upl/srv/www/auction/public/upload7/',
                      'local:///': '/upl/srv/www/223/smsp/',
                      'local3:///': '/upl/srv/www/sectionks-archive/data/upload3/',
                      'local6:///': '/upl/srv/www/sectionks/data/upload6/'
                      }


