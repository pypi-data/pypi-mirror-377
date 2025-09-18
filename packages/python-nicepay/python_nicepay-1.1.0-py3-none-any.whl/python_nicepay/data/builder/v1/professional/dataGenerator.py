import json
from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.util.utilMerchantToken import MerchantToken


class DataGenerator:

    @staticmethod
    def getTransactionHeader():
        headerMap = {"Content-Type": "Application/JSON"}
        return headerMap

    @staticmethod
    def getTransactionBody(body, cartData, sellers):
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
        shopId = ConstantsGeneral.getShopId()
        userIp = ConstantsGeneral.getUserIp()
        callBackUrl = ConstantsGeneral.getCallbackUrl()
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
        bodyMap["deliveryPhone"] = "08123456789"
        bodyMap["deliveryAddr"] = "Jln. Dr. Saharjo No.88"
        bodyMap["deliveryCity"] = "South Jakarta"
        bodyMap["deliveryState"] = "DKI Jakarta"
        bodyMap["deliveryCountry"] = "Indonesia"
        bodyMap["deliveryPostCd"] = "10202"
        bodyMap["goodsNm"] = "TESTING PY V2"
        bodyMap["description"] = "This is testing transaction redirect - n1tr0"
        bodyMap["shopId"] = shopId
        bodyMap["userIP"] = userIp
        bodyMap["callBackUrl"] = callBackUrl
        bodyMap["dbProcessUrl"] = dbProcessUrl
        bodyMap["cartData"] = cartData
        bodyMap["sellers"] = sellers
        bodyMap["currency"] = currency
        bodyMap["merchantToken"] = merchantToken
        bodyMap.update(body)

        return bodyMap

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
