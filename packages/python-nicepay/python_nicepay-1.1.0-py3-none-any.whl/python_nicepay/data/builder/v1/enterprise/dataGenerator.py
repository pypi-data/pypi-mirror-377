import json
from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.util.utilLogging import Log
from python_nicepay.util.utilMerchantToken import MerchantToken

log = Log()


class DataGeneratorV1:

    @staticmethod
    def getTransactionHeaderV1():
        headerMap = {"Content-Type": "Application/JSON"}
        return headerMap

    @staticmethod
    def getTransactionBodyV1(body, cartData):
        bodyMap = {}
        a = json.dumps(body)
        dataBody = json.loads(a)
        amt = dataBody["amt"]
        b = json.dumps(cartData, indent=None, separators=(',', ':'))
        cartData = b.replace('"', '\"')

        if "referenceNo" in dataBody and dataBody["referenceNo"]:
            referenceNo = dataBody["referenceNo"]
        else:
            random = datetime.now().strftime("%Y%m%d%H%M%S")
            referenceNo = "Nice" + random

        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()
        # merchantToken = MerchantToken.getMerchantToken(timestamp, iMid, referenceNo, amt, merchantKey)
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{referenceNo}{amt}{merchantKey}")
        currency = ConstantsGeneral.getCurrency()
        dbProcessUrl = ConstantsGeneral.getDbProcessUrl()
        callbackUrl = ConstantsGeneral.getCallbackUrl()
        billingPhone = ConstantsGeneral.getBillingPhone()
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
        bodyMap["callBackUrl"] = callbackUrl
        bodyMap["cartData"] = cartData
        bodyMap["currency"] = currency
        bodyMap["merchantToken"] = merchantToken
        bodyMap.update(body)

        return bodyMap

    # @staticmethod
    # def getPaymentBody(body):
    #     bodyMap = {}
    #     callbackUrl = ConstantsGeneral.getCallbackUrl()
    #     iMid = ConstantsGeneral.getImid()
    #     merchantKey = ConstantsGeneral.getMerchantKey()
    #
    #     bodyMap.update(body)
    #     a = json.dumps(bodyMap)
    #     data = json.loads(a)
    #     timestamp = data["timeStamp"]
    #     referenceNo = data["referenceNo"]
    #     amt = data["amt"]
    #     merchantToken = MerchantToken.getMerchantToken(f"{timestamp}{iMid}{referenceNo}{amt}{merchantKey}")
    #
    #     bodyMap["callBackUrl"] = callbackUrl
    #     bodyMap["merchantToken"] = merchantToken
    #     b = json.dumps(bodyMap)
    #     cleanJson = json.loads(b)
    #
    #     del cleanJson["amt"]
    #     del cleanJson["referenceNo"]
    #
    #     print(cleanJson)
    #     # finalData = urllib.parse.urlencode(cleanJson)
    #     return cleanJson

    @staticmethod
    def getInquiryBodyV1(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        referenceNo = data["referenceNo"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{referenceNo}{amt}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap

    @staticmethod
    def getCancelBodyV1(body):
        bodyMap = {}
        iMid = ConstantsGeneral.getImid()
        merchantKey = ConstantsGeneral.getMerchantKey()

        bodyMap.update(body)
        a = json.dumps(bodyMap)
        data = json.loads(a)
        tXid = data["tXid"]
        amt = data["amt"]
        merchantToken = MerchantToken.getMerchantToken(f"{iMid}{tXid}{amt}{merchantKey}")

        bodyMap["iMid"] = iMid
        bodyMap["merchantToken"] = merchantToken

        return bodyMap