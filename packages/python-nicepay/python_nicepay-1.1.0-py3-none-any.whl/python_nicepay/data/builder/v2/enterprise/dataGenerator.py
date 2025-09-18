import json
from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.util.utilLogging import Log
from python_nicepay.util.utilMerchantToken import MerchantToken

log = Log()


class DataGenerator:

    @staticmethod
    def getTransactionHeader():
        headerMap = {"Content-Type": "Application/JSON"}
        return headerMap

    @staticmethod
    def getTransactionBody(body, cartData):
        bodyMap = {}
        a = json.dumps(body)
        dataBody = json.loads(a)
        amt = dataBody["amt"]
        b = json.dumps(cartData, indent=None, separators=(',', ':'))
        cartData = b.replace('"', '\"')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        referenceNo = "OrdNo" + timestamp

        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()
        # merchantToken = MerchantToken.getMerchantToken(timestamp, iMid, referenceNo, amt, merchantKey)
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{referenceNo}{amt}{merchantKey}")
        currency = ConstantsGeneral.getCurrency()
        dbProcessUrl = ConstantsGeneral.getDbProcessUrl()
        billingPhone = ConstantsGeneral.getBillingPhone()
        bodyMap["timeStamp"] = timestamp
        bodyMap["iMid"] = iMid
        bodyMap["referenceNo"] = referenceNo
        bodyMap["billingNm"] = "John Doe"
        bodyMap["billingPhone"] = billingPhone
        bodyMap["billingEmail"] = "john.doe@example.com"
        bodyMap["billingAddr"] = "Jln. Raya Casablanca Kav.88"
        bodyMap["billingCity"] = "South Jakarta"
        bodyMap["billingState"] = "DKI Jakarta"
        bodyMap["billingCountry"] = "Indonesia"
        bodyMap["billingPostCd"] = "10200"
        bodyMap["deliveryNm"] = "Merchant's Name"
        bodyMap["deliveryPhone"] = "08123456789"
        bodyMap["deliveryAddr"] = "Jln. Dr. Saharjo No.88"
        bodyMap["deliveryCity"] = "South Jakarta"
        bodyMap["deliveryState"] = "DKI Jakarta"
        bodyMap["deliveryCountry"] = "Indonesia"
        bodyMap["deliveryPostCd"] = "10202"
        bodyMap["goodsNm"] = "TESTING PY V2"
        bodyMap["description"] = "This is testing transaction - n1tr0"
        bodyMap["shopId"] = ""
        bodyMap["dbProcessUrl"] = dbProcessUrl
        bodyMap["cartData"] = cartData
        bodyMap["currency"] = currency
        bodyMap["merchantToken"] = merchantToken
        bodyMap.update(body)

        return bodyMap

    @staticmethod
    def getPayloanBody(body, cartData, sellers):
        bodyMap = {}
        a = json.dumps(body)
        dataBody = json.loads(a)
        amt = dataBody["amt"]
        b = json.dumps(cartData, indent=None, separators=(',', ':'))
        cartData = b.replace('"', '\"')
        c = json.dumps(sellers, indent=None, separators=(',', ':'))
        sellers = c.replace('"', '\"')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        referenceNo = "OrdNo" + timestamp

        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{referenceNo}{amt}{merchantKey}")
        currency = ConstantsGeneral.getCurrency()
        dbProcessUrl = ConstantsGeneral.getDbProcessUrl()

        bodyMap["timeStamp"] = timestamp
        bodyMap["iMid"] = iMid
        bodyMap["referenceNo"] = referenceNo
        bodyMap["billingNm"] = "John Doe"
        bodyMap["billingPhone"] = "08123456789"
        bodyMap["billingEmail"] = "john.doe@example.com"
        bodyMap["billingAddr"] = "Jln. Raya Casablanca Kav.88"
        bodyMap["billingCity"] = "South Jakarta"
        bodyMap["billingState"] = "DKI Jakarta"
        bodyMap["billingCountry"] = "Indonesia"
        bodyMap["billingPostCd"] = "10200"
        bodyMap["deliveryNm"] = "Merchant's Name"
        bodyMap["deliveryPhone"] = "081227619520"
        bodyMap["deliveryAddr"] = "Jln. Dr. Saharjo No.88"
        bodyMap["deliveryCity"] = "South Jakarta"
        bodyMap["deliveryState"] = "DKI Jakarta"
        bodyMap["deliveryCountry"] = "Indonesia"
        bodyMap["deliveryPostCd"] = "10202"
        bodyMap["goodsNm"] = "TESTING PY V2"
        bodyMap["description"] = "This Is Testing Transaction By n1tr0"
        bodyMap["shopId"] = ""
        bodyMap["dbProcessUrl"] = dbProcessUrl
        bodyMap["cartData"] = cartData
        bodyMap["sellers"] = sellers
        bodyMap["currency"] = currency
        bodyMap["merchantToken"] = merchantToken
        bodyMap.update(body)

        return bodyMap

    @staticmethod
    def getPaymentBody(body):
        bodyMap = {}
        callbackUrl = ConstantsGeneral.getCallbackUrl()
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        timestamp = data["timeStamp"]
        referenceNo = data["referenceNo"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{referenceNo}{amt}{merchantKey}")

        bodyMap["callBackUrl"] = callbackUrl
        bodyMap["merchantToken"] = merchantToken
        b = json.dumps(bodyMap)
        cleanJson = json.loads(b)

        del cleanJson["amt"]
        del cleanJson["referenceNo"]

        print(cleanJson)
        # finalData = urllib.parse.urlencode(cleanJson)
        return cleanJson

    @staticmethod
    def getInquiryBody(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        referenceNo = data["referenceNo"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{referenceNo}{amt}{merchantKey}")

        bodyMap["timeStamp"] = timestamp
        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getCancelBody(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        tXid = data["tXid"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{tXid}{amt}{merchantKey}")

        bodyMap["timeStamp"] = timestamp
        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getPayoutRegBody(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        accountNo = data["accountNo"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{amt}{accountNo}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["timeStamp"] = timestamp
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getPayoutApproveBody(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        tXid = data["tXid"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{tXid}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["timeStamp"] = timestamp
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getPayoutReject(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        tXid = data["tXid"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{tXid}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["timeStamp"] = timestamp
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getPayoutCancel(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        tXid = data["tXid"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{tXid}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["timeStamp"] = timestamp
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getPayoutInquiry(body):
        bodyMap = {}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        accountNo = data["accountNo"]
        tXid = data["tXid"]
        merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{tXid}{accountNo}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["timeStamp"] = timestamp
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getVAFixedOpenReg(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        customerId = data["customerId"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{customerId}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken
        # finalData = urllib.parse.urlencode(bodyMap)
        return bodyMap

    @staticmethod
    def getVAFixedOpenCustInq(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        customerId = data["customerId"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{customerId}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getVAFixedOpenDepositInq(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        vacctNo = data["vacctNo"]
        startDt = data["startDt"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{vacctNo}{startDt}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getVAFixedOpenUpdate(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        customerId = data["customerId"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{customerId}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap
