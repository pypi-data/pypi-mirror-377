import json
from datetime import datetime

from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.util.utilSignature import Signature


class dataGenerator:
    @staticmethod
    def getOAUTHHeader():
        headersMap = {}
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "+07:00"
        clientKey = ConstantsGeneral.getClientKey()
        privateKey = ConstantsGeneral.getPrivateKey()

        headersMap["Content-Type"] = "Application/JSON"
        stringToSign = f"{clientKey}|{timestamp}"
        signatureAccessToken = Signature.signSHA256RSA(stringToSign, privateKey)
        headersMap["X-TIMESTAMP"] = timestamp
        headersMap["X-CLIENT-KEY"] = clientKey
        headersMap["X-SIGNATURE"] = signatureAccessToken

        return headersMap

    @staticmethod
    def getTransactionHeader(accessToken, data, endpoint, httpMethod):
        headersMap = {}
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "+07:00"
        clientKey = ConstantsGeneral.getClientKey()
        secretKey = ConstantsGeneral.getClientSecret()
        externalId = "ordNo" + datetime.now().strftime("%Y%m%d%H%M%S")

        headersMap["Content-Type"] = "Application/JSON"
        hashData = Signature.sha256EncodeHex(json.dumps(data))
        signature = Signature.getSignature(accessToken, hashData, endpoint, timestamp, secretKey, httpMethod)
        headersMap["Authorization"] = f"Bearer {accessToken}"
        headersMap["X-TIMESTAMP"] = timestamp
        headersMap["X-PARTNER-ID"] = clientKey
        headersMap["X-SIGNATURE"] = signature
        headersMap["X-EXTERNAL-ID"] = externalId
        headersMap["CHANNEL-ID"] = clientKey + "01"

        return headersMap
