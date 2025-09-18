class DirectDebit:
    def __init__(self,
                 partnerReferenceNo,
                 merchantId,
                 subMerchantId,
                 externalStoreId,
                 validUpTo,
                 pointOfInitiation,
                 amount,
                 urlParam,
                 additionalInfo):
        self.partnerReferenceNo = partnerReferenceNo
        self.merchantId = merchantId
        self.subMerchantId = subMerchantId
        self.externalStoreId = externalStoreId
        self.validUpTo = validUpTo
        self.pointOfInitiation = pointOfInitiation
        self.amount = amount
        self.urlParam = urlParam
        self.additionalInfo = additionalInfo

    def jsonDirectDebit(self):
        return ({
            "partnerReferenceNo": self.partnerReferenceNo,
            "merchantId": self.merchantId,
            "subMerchantId": self.subMerchantId,
            "externalStoreId":  self.externalStoreId,
            "validUpTo": self.validUpTo,
            "pointOfInitiation": self.pointOfInitiation,
            "amount": self.amount,
            "urlParam": self.urlParam,
            "additionalInfo": self.additionalInfo
        })
class BuilderDirectDebit:
    def __init__(self):
        self.partnerReferenceNo = None
        self.merchantId = None
        self.subMerchantId = None
        self.externalStoreId = None
        self.validUpTo = None
        self.pointOfInitiation = None
        self.amount = None
        self.urlParam = None
        self.additionalInfo = None

    def setPartnerReferenceNo(self, partnerReferenceNo):
        self.partnerReferenceNo = partnerReferenceNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setSubMerchantId(self, subMerchantId):
        self.subMerchantId = subMerchantId
        return self

    def setExternalStoreId(self, externalStoreId):
        self.externalStoreId = externalStoreId
        return self

    def setValidUpTo(self, validUpTo):
        self.validUpTo = validUpTo
        return self

    def setPointOfInitiation(self, pointOfInitiation):
        self.pointOfInitiation = pointOfInitiation
        return self

    def setAmount(self, amount):
        self.amount = amount
        return self

    def setUrlParam(self, urlParam):
        self.urlParam = urlParam
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildDirectDebit(BuilderDirectDebit):
    def build(self):
        return DirectDebit(
            self.partnerReferenceNo,
            self.merchantId,
            self.subMerchantId,
            self.externalStoreId,
            self.validUpTo,
            self.pointOfInitiation,
            self.amount,
            self.urlParam,
            self.additionalInfo
        )

class DirectDebitInquiry:
    def __init__(self,
                 merchantId,
                 subMerchantId,
                 originalPartnerReferenceNo,
                 originalReferenceNo,
                 serviceCode,
                 transactionDate,
                 amount,
                 additionalInfo):
        self.merchantId = merchantId
        self.subMerchantId = subMerchantId
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.serviceCode = serviceCode
        self.transactionDate = transactionDate
        self.amount = amount
        self.additionalInfo = additionalInfo

    def jsonDirectDebitInquiry(self):
        return ({
            "merchantId": self.merchantId,
            "subMerchantId": self.subMerchantId,
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "serviceCode": self.serviceCode,
            "transactionDate": self.transactionDate,
            "amount": self.amount,
            "additionalInfo": self.additionalInfo
        })
class BuilderDirectDebitInquiry:
    def __init__(self):
        self.merchantId = None
        self.subMerchantId = None
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.serviceCode = None
        self.transactionDate = None
        self.amount = None
        self.additionalInfo = None

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setSubMerchantId(self, subMerchantId):
        self.subMerchantId = subMerchantId
        return self

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setServiceCode(self, serviceCode):
        self.serviceCode = serviceCode
        return self

    def setTransactionDate(self, transactionDate):
        self.transactionDate = transactionDate
        return self

    def setAmount(self, amount):
        self.amount = amount
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildDirectDebitInquiry(BuilderDirectDebitInquiry):
    def build(self):
        return DirectDebitInquiry(
            self.merchantId,
            self.subMerchantId,
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.serviceCode,
            self.transactionDate,
            self.amount,
            self.additionalInfo
        )

class DirectDebitRefund:
    def __init__(self,
                 partnerRefundNo,
                 merchantId,
                 subMerchantId,
                 originalPartnerReferenceNo,
                 originalReferenceNo,
                 externalStoreId,
                 reason,
                 refundAmount,
                 additionalInfo):
        self.partnerRefundNo = partnerRefundNo
        self.merchantId = merchantId
        self.subMerchantId = subMerchantId
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.externalStoreId = externalStoreId
        self.reason = reason
        self.refundAmount = refundAmount
        self.additionalInfo = additionalInfo

    def jsonDirectDebitRefund(self):
        return ({
            "partnerRefundNo": self.partnerRefundNo,
            "merchantId": self.merchantId,
            "subMerchantId": self.subMerchantId,
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "externalStoreId": self.externalStoreId,
            "reason": self.reason,
            "refundAmount": self.refundAmount,
            "additionalInfo": self.additionalInfo
        })
class BuilderDirectDebitRefund:
    def __init__(self):
        self.partnerRefundNo = None
        self.merchantId = None
        self.subMerchantId = None
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.externalStoreId = None
        self.reason = None
        self.refundAmount = None
        self.additionalInfo = None

    def setPartnerRefundNo(self, partnerRefundNo):
        self.partnerRefundNo = partnerRefundNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setSubMerchantId(self, subMerchantId):
        self.subMerchantId = subMerchantId
        return self

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setExternalStoreId(self, externalStoreId):
        self.externalStoreId = externalStoreId
        return self

    def setReason(self, reason):
        self.reason = reason
        return self

    def setRefundAmount(self, refundAmount):
        self.refundAmount = refundAmount
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildDirectDebitRefund(BuilderDirectDebitRefund):
    def build(self):
        return DirectDebitRefund(
            self.partnerRefundNo,
            self.merchantId,
            self.subMerchantId,
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.externalStoreId,
            self.reason,
            self.refundAmount,
            self.additionalInfo
        )


