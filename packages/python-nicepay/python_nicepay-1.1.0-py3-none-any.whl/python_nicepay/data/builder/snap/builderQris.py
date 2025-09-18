class Qris:
    def __init__(self,
                 merchantId,
                 partnerReferenceNo,
                 storeId,
                 validityPeriod,
                 amount,
                 additionalInfo):
        self.merchantId = merchantId
        self.partnerReferenceNo = partnerReferenceNo
        self.storeId = storeId
        self.validityPeriod = validityPeriod
        self.amount = amount
        self.additionalInfo = additionalInfo

    def jsonQris(self):
        return ({
            "merchantId": self.merchantId,
            "partnerReferenceNo": self.partnerReferenceNo,
            "storeId": self.storeId,
            "validityPeriod": self.validityPeriod,
            "amount": self.amount,
            "additionalInfo": self.additionalInfo
        })
class BuilderQris:
    def __init__(self):
        self.merchantId = None
        self.partnerReferenceNo = None
        self.storeId = None
        self.validityPeriod = None
        self.amount = None
        self.additionalInfo = None

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setPartnerReferenceNo(self, partnerReferenceNo):
        self.partnerReferenceNo = partnerReferenceNo
        return self

    def setStoreId(self, storeId):
        self.storeId = storeId
        return self

    def setValidityPeriod(self, validityPeriod):
        self.validityPeriod = validityPeriod
        return self

    def setAmount(self, amount):
        self.amount = amount
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildQris(BuilderQris):
    def build(self):
        return Qris(
            self.merchantId,
            self.partnerReferenceNo,
            self.storeId,
            self.validityPeriod,
            self.amount,
            self.additionalInfo
        )

class QrisInquiry:
    def __init__(self,
                 merchantId,
                 externalStoreId,
                 originalReferenceNo,
                 originalPartnerReferenceNo,
                 serviceCode,
                 additionalInfo):
        self.merchantId = merchantId
        self.externalStoreId = externalStoreId
        self.originalReferenceNo = originalReferenceNo
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.serviceCode = serviceCode
        self.additionalInfo = additionalInfo

    def jsonQrisInquiry(self):
        return ({
            "merchantId": self.merchantId,
            "externalStoreId": self.externalStoreId,
            "originalReferenceNo": self.originalReferenceNo,
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "serviceCode": self.serviceCode,
            "additionalInfo": self.additionalInfo
        })
class BuilderQrisInquiry:
    def __init__(self):
        self.merchantId = None
        self.externalStoreId = None
        self.originalReferenceNo = None
        self.originalPartnerReferenceNo = None
        self.serviceCode = None
        self.additionalInfo = None

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setExternalStoreId(self, externalStoreId):
        self.externalStoreId = externalStoreId
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setServiceCode(self, serviceCode):
        self.serviceCode = serviceCode
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildQrisInquiry(BuilderQrisInquiry):
    def build(self):
        return QrisInquiry(
            self.merchantId,
            self.externalStoreId,
            self.originalReferenceNo,
            self.originalPartnerReferenceNo,
            self.serviceCode,
            self.additionalInfo
        )


class QrisRefund:
    def __init__(self,
                 merchantId,
                 externalStoreId,
                 originalReferenceNo,
                 originalPartnerReferenceNo,
                 partnerRefundNo,
                 refundAmount,
                 reason,
                 additionalInfo):
        self.merchantId = merchantId
        self.externalStoreId = externalStoreId
        self.originalReferenceNo = originalReferenceNo
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.partnerRefundNo = partnerRefundNo
        self.refundAmount = refundAmount
        self.reason = reason
        self.additionalInfo = additionalInfo

    def jsonQrisRefund(self):
        return ({
            "merchantId": self.merchantId,
            "externalStoreId": self.externalStoreId,
            "originalReferenceNo": self.originalReferenceNo,
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "partnerRefundNo": self.partnerRefundNo,
            "refundAmount": self.refundAmount,
            "reason": self.reason,
            "additionalInfo": self.additionalInfo
        })
class BuilderQrisRefund:
    def __init__(self):
        self.merchantId = None
        self.externalStoreId = None
        self.originalReferenceNo = None
        self.originalPartnerReferenceNo = None
        self.partnerRefundNo = None
        self.refundAmount = None
        self.reason = None
        self.additionalInfo = None

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setExternalStoreId(self, externalStoreId):
        self.externalStoreId = externalStoreId
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setPartnerRefundNo(self, partnerRefundNo):
        self.partnerRefundNo = partnerRefundNo
        return self

    def setRefundAmount(self, refundAmount):
        self.refundAmount = refundAmount
        return self

    def setReason(self, reason):
        self.reason = reason
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildQrisRefund(BuilderQrisRefund):
    def build(self):
        return QrisRefund(
            self.merchantId,
            self.externalStoreId,
            self.originalReferenceNo,
            self.originalPartnerReferenceNo,
            self.partnerRefundNo,
            self.refundAmount,
            self.reason,
            self.additionalInfo
        )
