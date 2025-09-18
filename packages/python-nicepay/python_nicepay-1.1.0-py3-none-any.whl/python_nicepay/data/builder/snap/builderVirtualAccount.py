# CREATE VA SECTION
class CreateVA:
    def __init__(self,
                 partnerServiceId,
                 customerNo,
                 virtualAccountNo,
                 virtualAccountName,
                 trxId,
                 totalAmount,
                 additionalInfo):
        self.partnerServiceId = partnerServiceId
        self.customerNo = customerNo
        self.virtualAccountNo = virtualAccountNo
        self.virtualAccountName = virtualAccountName
        self.trxId = trxId
        self.totalAmount = totalAmount
        self.additionalInfo = additionalInfo

    def jsonVACreate(self):
        return ({
            "partnerServiceId": self.partnerServiceId,
            "customerNo": self.customerNo,
            "virtualAccountNo": self.virtualAccountNo,
            "virtualAccountName": self.virtualAccountName,
            "trxId": self.trxId,
            "totalAmount": self.totalAmount,
            "additionalInfo": self.additionalInfo
        })
class BuilderCreateVA:
    def __init__(self):
        self.partnerServiceId = None
        self.customerNo = None
        self.virtualAccountNo = None
        self.virtualAccountName = None
        self.trxId = None
        self.totalAmount = None
        self.additionalInfo = None

    def setPartnerServiceId(self, partnerServiceId):
        self.partnerServiceId = partnerServiceId
        return self

    def setCustomerNo(self, customerNo):
        self.customerNo = customerNo
        return self

    def setVirtualAccountNo(self, virtualAccountNo):
        self.virtualAccountNo = virtualAccountNo
        return self

    def setVirtualAccountName(self, virtualAccountName):
        self.virtualAccountName = virtualAccountName
        return self

    def setTrxId(self, trxId):
        self.trxId = trxId
        return self

    def setTotalAmount(self, totalAmount):
        self.totalAmount = totalAmount
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildCreateVA(BuilderCreateVA):
    def build(self):
        return CreateVA(
            self.partnerServiceId,
            self.customerNo,
            self.virtualAccountNo,
            self.virtualAccountName,
            self.trxId,
            self.totalAmount,
            self.additionalInfo
        )

class InquiryVA:
    def __init__(self,
                 partnerServiceId,
                 customerNo,
                 virtualAccountNo,
                 inquiryRequestId,
                 additionalInfo):
        self.partnerServiceId = partnerServiceId
        self.customerNo = customerNo
        self.virtualAccountNo = virtualAccountNo
        self.inquiryRequestId = inquiryRequestId
        self.additionalInfo = additionalInfo

    def jsonVAInquiry(self):
        return ({
            "partnerServiceId": self.partnerServiceId,
            "customerNo": self.customerNo,
            "virtualAccountNo": self.virtualAccountNo,
            "inquiryRequestId": self.inquiryRequestId,
            "additionalInfo": self.additionalInfo
        })
class BuilderInquiryVA:
    def __init__(self):
        self.partnerServiceId = None
        self.customerNo = None
        self.virtualAccountNo = None
        self.inquiryRequestId = None
        self.additionalInfo = None

    def setPartnerServiceId(self, partnerServiceId):
        self.partnerServiceId = partnerServiceId
        return self

    def setCustomerNo(self, customerNo):
        self.customerNo = customerNo
        return self

    def setVirtualAccountNo(self, virtualAccountNo):
        self.virtualAccountNo = virtualAccountNo
        return self

    def setInquiryRequestId(self, inquiryRequestId):
        self.inquiryRequestId = inquiryRequestId
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildInquiryVA(BuilderInquiryVA):
    def build(self):
        return InquiryVA(
            self.partnerServiceId,
            self.customerNo,
            self.virtualAccountNo,
            self.inquiryRequestId,
            self.additionalInfo
        )

class CancelVA:
    def __init__(self,
                 partnerServiceId,
                 customerNo,
                 virtualAccountNo,
                 trxId,
                 additionalInfo):
        self.partnerServiceId = partnerServiceId
        self.customerNo = customerNo
        self.virtualAccountNo = virtualAccountNo
        self.trxId = trxId
        self.additionalInfo = additionalInfo

    def jsonVACancel(self):
        return ({
            "partnerServiceId": self.partnerServiceId,
            "customerNo": self.customerNo,
            "virtualAccountNo": self.virtualAccountNo,
            "trxId": self.trxId,
            "additionalInfo": self.additionalInfo
        })
class BuilderCancelVA:
    def __init__(self):
        self.partnerServiceId = None
        self.customerNo = None
        self.virtualAccountNo = None
        self.trxId = None
        self.additionalInfo = None

    def setPartnerServiceId(self, partnerServiceId):
        self.partnerServiceId = partnerServiceId
        return self

    def setCustomerNo(self, customerNo):
        self.customerNo = customerNo
        return self

    def setVirtualAccountNo(self, virtualAccountNo):
        self.virtualAccountNo = virtualAccountNo
        return self

    def setTrxId(self, trxId):
        self.trxId = trxId
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildCancelVA(BuilderCancelVA):
    def build(self):
        return CancelVA(
            self.partnerServiceId,
            self.customerNo,
            self.virtualAccountNo,
            self.trxId,
            self.additionalInfo
        )
