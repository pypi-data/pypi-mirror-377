class ConstantsGeneral:

    _SANDBOX_BASE_URL = "https://dev.nicepay.co.id/nicepay"
    _STAGING_BASE_URL = "https://staging.nicepay.co.id/nicepay"
    _PRODUCTION_BASE_URL = "https://www.nicepay.co.id/nicepay"

    CLOUD_SANDBOX_BASE_URL = "https://dev-services.nicepay.co.id/nicepay/"
    CLOUD_PRODUCTION_BASE_URL = "https://services.nicepay.co.id/nicepay/"

    # SNAP
    _PRIVATE_KEY = "_YOUR_PRIVATE_KEY"
    _CLIENT_KEY = "_YOUR_CLIENT_KEY"
    _CLIENT_SECRET = "_YOUR_CLIENT_SECRET"

    #V1 & V2
    _I_MID = "_YOUR_I_MID"
    _MERCHANT_KEY = "_YOUR_MERCHANT_KEY"
    _PAY_METHOD_CREDIT_CARD = "01"
    _PAY_METHOD_VIRTUAL_ACCOUNT = "02"
    _PAY_METHOD_CONVENIENCE_STORE = "03"
    _PAY_METHOD_DIRECT_DEBIT = "04"
    _PAY_METHOD_E_WALLET = "05"
    _PAY_METHOD_PAYLOAN = "06"
    _PAY_METHOD_PAYOUT = "07"
    _PAY_METHOD_QRIS = "08"
    _PAY_METHOD_GPN = "09"
    _CURRENCY = "IDR"
    _CALLBACK_URL = "https://dev.nicepay.co.id/IONPAY_CLIENT/paymentResult.jsp"
    _DB_PROCESS_URL = "_YOUR_DB_PROCESS_URL"
    _USER_IP = "127.0.0.1"
    _USER_SESSION_ID = ""
    _USER_AGENT = ""
    _USER_LANGUAGE = ""
    _SHOP_ID = "NICEPAY"
    _BILLING_PHONE = '08123456789'

    # Getter
    @staticmethod
    def getSandboxBaseUrl():
        return ConstantsGeneral._SANDBOX_BASE_URL

    @staticmethod
    def getStagingBaseUrl():
        return ConstantsGeneral._STAGING_BASE_URL

    @staticmethod
    def getProductionBaseUrl():
        return ConstantsGeneral._PRODUCTION_BASE_URL

    @staticmethod
    def getPrivateKey():
        return ConstantsGeneral._PRIVATE_KEY

    @staticmethod
    def getClientKey():
        return ConstantsGeneral._CLIENT_KEY

    @staticmethod
    def getClientSecret():
        return ConstantsGeneral._CLIENT_SECRET

    #V2
    @staticmethod
    def getImid():
        return ConstantsGeneral._I_MID

    @staticmethod
    def getMerchantKey():
        return ConstantsGeneral._MERCHANT_KEY

    @staticmethod
    def getPayMethodCreditCard():
        return ConstantsGeneral._PAY_METHOD_CREDIT_CARD

    @staticmethod
    def getPayMethodVirtualAccount():
        return ConstantsGeneral._PAY_METHOD_VIRTUAL_ACCOUNT

    @staticmethod
    def getPayMethodConvenienceStore():
        return ConstantsGeneral._PAY_METHOD_CONVENIENCE_STORE

    @staticmethod
    def getPayMethodDirectDebit():
        return ConstantsGeneral._PAY_METHOD_DIRECT_DEBIT

    @staticmethod
    def getPayMethodEWallet():
        return ConstantsGeneral._PAY_METHOD_E_WALLET

    @staticmethod
    def getPayMethodPayloan():
        return ConstantsGeneral._PAY_METHOD_PAYLOAN

    @staticmethod
    def getPayMethodPayout():
        return ConstantsGeneral._PAY_METHOD_PAYOUT

    @staticmethod
    def getPayMethodQris():
        return ConstantsGeneral._PAY_METHOD_QRIS

    @staticmethod
    def getPayMethodGpn():
        return ConstantsGeneral._PAY_METHOD_GPN

    @staticmethod
    def getCurrency():
        return ConstantsGeneral._CURRENCY

    @staticmethod
    def getCallbackUrl():
        return ConstantsGeneral._CALLBACK_URL

    @staticmethod
    def getDbProcessUrl():
        return ConstantsGeneral._DB_PROCESS_URL

    @staticmethod
    def getUserIp():
        return ConstantsGeneral._USER_IP

    @staticmethod
    def getShopId():
        return ConstantsGeneral._SHOP_ID

    @staticmethod
    def getBillingPhone():
        return ConstantsGeneral._BILLING_PHONE

    # Setter
    @staticmethod
    def setSandboxBaseUrl(value):
        ConstantsGeneral._SANDBOX_BASE_URL = value

    @staticmethod
    def setStagingBaseUrl(value):
        ConstantsGeneral._STAGING_BASE_URL = value

    @staticmethod
    def setProductionBaseUrl(value):
        ConstantsGeneral._PRODUCTION_BASE_URL = value

    @staticmethod
    def setPrivateKey(value):
        ConstantsGeneral._PRIVATE_KEY = value

    @staticmethod
    def setClientKey(value):
        ConstantsGeneral._CLIENT_KEY = value

    @staticmethod
    def setClientSecret(value):
        ConstantsGeneral._CLIENT_SECRET = value

    @staticmethod
    def setImid(value):
        ConstantsGeneral._I_MID = value

    @staticmethod
    def setMerchantKey(value):
        ConstantsGeneral._MERCHANT_KEY = value

    @staticmethod
    def setPayMethodCreditCard(value):
        ConstantsGeneral._PAY_METHOD_CREDIT_CARD = value

    @staticmethod
    def setPayMethodVirtualAccount(value):
        ConstantsGeneral._PAY_METHOD_VIRTUAL_ACCOUNT = value

    @staticmethod
    def setPayMethodConvenienceStore(value):
        ConstantsGeneral._PAY_METHOD_CONVENIENCE_STORE = value

    @staticmethod
    def setPayMethodDirectDebit(value):
        ConstantsGeneral._PAY_METHOD_DIRECT_DEBIT = value

    @staticmethod
    def setPayMethodEWallet(value):
        ConstantsGeneral._PAY_METHOD_E_WALLET = value

    @staticmethod
    def setPayMethodPayloan(value):
        ConstantsGeneral._PAY_METHOD_PAYLOAN = value

    @staticmethod
    def setPayMethodPayout(value):
        ConstantsGeneral._PAY_METHOD_PAYOUT = value

    @staticmethod
    def setPayMethodQris(value):
        ConstantsGeneral._PAY_METHOD_QRIS = value

    @staticmethod
    def setPayMethodGpn(value):
        ConstantsGeneral._PAY_METHOD_GPN = value

    @staticmethod
    def setCurrency(value):
        ConstantsGeneral._CURRENCY = value

    @staticmethod
    def setCallbackUrl(value):
        ConstantsGeneral._CALLBACK_URL = value

    @staticmethod
    def setDbProcessUrl(value):
        ConstantsGeneral._DB_PROCESS_URL = value

    @staticmethod
    def setUserIp(value):
        ConstantsGeneral._USER_IP = value

    @staticmethod
    def setShopId(value):
        ConstantsGeneral._SHOP_ID = value

    @staticmethod
    def setBillingPhone(value):
        ConstantsGeneral._BILLING_PHONE = value

    # Setter for merchant
    @staticmethod
    def setNonSnapConfiguration(imId, merchantKey, dbProcessUrl, callbackUrl):
        ConstantsGeneral._I_MID = imId
        ConstantsGeneral._MERCHANT_KEY = merchantKey
        ConstantsGeneral._DB_PROCESS_URL = dbProcessUrl
        ConstantsGeneral._CALLBACK_URL = callbackUrl

    @staticmethod
    def setSnapConfiguration(clientKey, clientSecret, privateKey):
        ConstantsGeneral._CLIENT_KEY = clientKey
        ConstantsGeneral._CLIENT_SECRET = clientSecret
        ConstantsGeneral._PRIVATE_KEY = privateKey