class Config:
    MONGO_URL = 'mongodb://root:example@localhost:27017/smev_int?authSource=admin'
    ADAPTER_SETTINGS = {
        'url': 'http://192.168.1.1:7575/ws?wsdl',
        'mnemonic': '112233',
        'test_mode': True
    }
    HOST = '0.0.0.0'
    PORT = '9003'
    API_KEY = 'abracadabra'
    API_KEY_HEADER = 'X-Auth-Token'
    RESPONSE_CHECK_TIMEOUT = 60
    DOCUMENT_IDENTIFIERS = {
        'FNSVipUL': 'СвЮЛ.ОГРН',
        'ESIARegister': 'request_id',
        'ESIARegisterCertificate': 'request_id',
    }
