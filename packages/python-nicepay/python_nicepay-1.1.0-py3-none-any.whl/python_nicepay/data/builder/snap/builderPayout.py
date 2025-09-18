class Payout:
    #Constructor
    def __init__(self,
                 partnerReferenceNo,
                 merchantId,
                 msId,
                 beneficiaryAccountNo,
                 beneficiaryName,
                 beneficiaryPhone,
                 beneficiaryCustomerResidence,
                 beneficiaryCustomerType,
                 beneficiaryPostalCode,
                 beneficiaryBankCode,
                 beneficiaryPOE,
                 beneficiaryDOE,
                 beneficiaryCoNo,
                 beneficiaryAddress,
                 beneficiaryAuthPhoneNumber,
                 beneficiaryMerCategory,
                 beneficiaryCoMgmtName,
                 beneficiaryCoShName,
                 payoutMethod,
                 reservedDt,
                 reservedTm,
                 deliveryId,
                 deliveryNm,
                 amount
                ):
        self.partnerReferenceNo = partnerReferenceNo
        self.merchantId = merchantId
        self.msId = msId
        self.beneficiaryAccountNo = beneficiaryAccountNo
        self.beneficiaryPhone = beneficiaryPhone
        self.beneficiaryName = beneficiaryName
        self.beneficiaryCustomerResidence = beneficiaryCustomerResidence
        self.beneficiaryCustomerType = beneficiaryCustomerType
        self.beneficiaryPostalCode = beneficiaryPostalCode
        self.beneficiaryBankCode = beneficiaryBankCode
        self.beneficiaryPOE = beneficiaryPOE
        self.beneficiaryDOE = beneficiaryDOE
        self.beneficiaryCoNo = beneficiaryCoNo
        self.beneficiaryAddress = beneficiaryAddress
        self.beneficiaryAuthPhoneNumber = beneficiaryAuthPhoneNumber
        self.beneficiaryMerCategory = beneficiaryMerCategory
        self.beneficiaryCoMgmtName = beneficiaryCoMgmtName
        self.beneficiaryCoShName = beneficiaryCoShName
        self.payoutMethod = payoutMethod
        self.reservedDt = reservedDt
        self.reservedTm = reservedTm
        self.deliveryId = deliveryId
        self.deliveryNm = deliveryNm
        self.amount = amount

    # Create body to json
    def jsonPayout(self):
        return ({
            "partnerReferenceNo": self.partnerReferenceNo,
            "merchantId": self.merchantId,
            "msId": self.msId,
            "beneficiaryAccountNo": self.beneficiaryAccountNo,
            "beneficiaryPhone": self.beneficiaryPhone,
            "beneficiaryName": self.beneficiaryName,
            "beneficiaryCustomerResidence": self.beneficiaryCustomerResidence,
            "beneficiaryCustomerType": self.beneficiaryCustomerType,
            "beneficiaryPostalCode": self.beneficiaryPostalCode,
            "beneficiaryBankCode": self.beneficiaryBankCode,
            "beneficiaryPOE": self.beneficiaryPOE,
            "beneficiaryDOE": self.beneficiaryDOE,
            "beneficiaryCoNo": self.beneficiaryCoNo,
            "beneficiaryAddress": self.beneficiaryAddress,
            "beneficiaryAuthPhoneNumber": self.beneficiaryAuthPhoneNumber,
            "beneficiaryMerCategory": self.beneficiaryMerCategory,
            "beneficiaryCoMgmtName": self.beneficiaryCoMgmtName,
            "beneficiaryCoShName": self.beneficiaryCoShName,
            "payoutMethod": self.payoutMethod,
            "reservedDt": self.reservedDt,
            "reservedTm": self.reservedTm,
            "deliveryId": self.deliveryId,
            "deliveryNm": self.deliveryNm,
            "amount": self.amount,

        })
class BuilderPayout:
    # Constructor
    def __init__(self):
        self.partnerReferenceNo = None
        self.merchantId = None
        self.msId = None
        self.beneficiaryAccountNo = None
        self.beneficiaryPhone = None
        self.beneficiaryName = None
        self.beneficiaryCustomerResidence = None
        self.beneficiaryCustomerType = None
        self.beneficiaryPostalCode = None
        self.beneficiaryBankCode = None
        self.beneficiaryPOE = None
        self.beneficiaryDOE = None
        self.beneficiaryCoNo = None
        self.beneficiaryAddress = None
        self.beneficiaryAuthPhoneNumber = None
        self.beneficiaryMerCategory = None
        self.beneficiaryCoMgmtName = None
        self.beneficiaryCoShName = None
        self.payoutMethod = None
        self.reservedDt = None
        self.reservedTm = None
        self.deliveryId = None
        self.deliveryNm = None
        self.amount = None

    #Setter
    def setPartnerReferenceNo(self, partnerReferenceNo):
        self.partnerReferenceNo = partnerReferenceNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self
    def setMsId(self, msId):
        self.msId = msId
        return self
    def setBeneficiaryAccountNo(self, beneficiaryAccountNo):
        self.beneficiaryAccountNo = beneficiaryAccountNo
        return self

    def setBeneficiaryName(self, beneficiaryName):
        self.beneficiaryName = beneficiaryName
        return self

    def setBeneficiaryPhone(self, beneficiaryPhone):
        self.beneficiaryPhone = beneficiaryPhone
        return self

    def setBeneficiaryCustomerResidence(self, beneficiaryCustomerResidence):
        self.beneficiaryCustomerResidence = beneficiaryCustomerResidence
        return self

    def setBeneficiaryCustomerType(self, beneficiaryCustomerType):
        self.beneficiaryCustomerType = beneficiaryCustomerType
        return self

    def setBeneficiaryPostalCode(self, beneficiaryPostalCode):
        self.beneficiaryPostalCode = beneficiaryPostalCode
        return self

    def setBeneficiaryBankCode(self, beneficiaryBankCode):
        self.beneficiaryBankCode = beneficiaryBankCode
        return self

    def setBeneficiaryPOE(self, beneficiaryPOE):
        self.beneficiaryPOE = beneficiaryPOE
        return self

    def setBeneficiaryDOE(self, beneficiaryDOE):
        self.beneficiaryDOE = beneficiaryDOE
        return self

    def setBeneficiaryCoNo(self, beneficiaryCoNo):
        self.beneficiaryCoNo = beneficiaryCoNo
        return self

    def setBeneficiaryAddress(self, beneficiaryAddress):
        self.beneficiaryAddress = beneficiaryAddress
        return self

    def setBeneficiaryAuthPhoneNumber(self, beneficiaryAuthPhoneNumber):
        self.beneficiaryAuthPhoneNumber = beneficiaryAuthPhoneNumber
        return self

    def setBeneficiaryMerCategory(self, beneficiaryMerCategory):
        self.beneficiaryMerCategory = beneficiaryMerCategory
        return self

    def setBeneficiaryCoMgmtName(self, beneficiaryCoMgmtName):
        self.beneficiaryCoMgmtName = beneficiaryCoMgmtName
        return self

    def setBeneficiaryCoShName(self, beneficiaryCoShName):
        self.beneficiaryCoShName = beneficiaryCoShName
        return self

    def setPayoutMethod(self, payoutMethod):
        self.payoutMethod = payoutMethod
        return self

    def setReservedDt(self, reservedDt):
        self.reservedDt = reservedDt
        return self

    def setReservedTm(self, reservedTm):
        self.reservedTm = reservedTm
        return self

    def setDeliveryId(self, deliveryId):
        self.deliveryId = deliveryId
        return self

    def setDeliveryNm(self, deliveryNm):
        self.deliveryNm = deliveryNm
        return self

    def setAmount(self, amount):
        self.amount = amount
        return self
class BuildPayout(BuilderPayout):
    def build(self):
        return Payout(
            self.partnerReferenceNo,
            self.merchantId,
            self.msId,
            self.beneficiaryAccountNo,
            self.beneficiaryName,
            self.beneficiaryPhone,
            self.beneficiaryCustomerResidence,
            self.beneficiaryCustomerType,
            self.beneficiaryPostalCode,
            self.beneficiaryBankCode,
            self.beneficiaryPOE,
            self.beneficiaryDOE,
            self.beneficiaryCoNo,
            self.beneficiaryAddress,
            self.beneficiaryAuthPhoneNumber,
            self.beneficiaryMerCategory,
            self.beneficiaryCoMgmtName,
            self.beneficiaryCoShName,
            self.payoutMethod,
            self.reservedDt,
            self.reservedTm,
            self.deliveryId,
            self.deliveryNm,
            self.amount,
        )

class PayoutInquiry:
    #Constructor
    def __init__(self,
                merchantId,
                originalPartnerReferenceNo,
                originalReferenceNo,
                beneficiaryAccountNo
                ):
        self.merchantId = merchantId
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.beneficiaryAccountNo = beneficiaryAccountNo


    # Create body to json
    def jsonPayoutInquiry(self):
        return ({
            "merchantId": self.merchantId,
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "beneficiaryAccountNo": self.beneficiaryAccountNo

        })
class BuilderPayoutInquiry:
    # Constructor
    def __init__(self):
        self.merchantId = None
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.beneficiaryAccountNo = None

    #Setter
    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
       self.originalPartnerReferenceNo = originalPartnerReferenceNo
       return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setBeneficiaryAccountNo(self, beneficiaryAccountNo):
        self.beneficiaryAccountNo = beneficiaryAccountNo
        return self
class BuildPayoutInquiry(BuilderPayoutInquiry):
    def build(self):
        return PayoutInquiry(
            self.merchantId,
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.beneficiaryAccountNo
        )

class PayoutApprove:
    def __init__(self,
                 originalPartnerReferenceNo,
                 originalReferenceNo,
                 merchantId):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.merchantId = merchantId

    def jsonPayoutApprove(self):
        return ({
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "merchantId": self.merchantId
        })
class BuilderPayoutApprove:
    def __init__(self):
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.merchantId = None

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self
class BuildPayoutApprove(BuilderPayoutApprove):
    def build(self):
        return PayoutApprove(
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.merchantId
        )

class PayoutBalanceInquiry:
    def __init__(self,
                 accountNo,
                 additionalInfo):
        self.accountNo = accountNo
        self.additionalInfo = additionalInfo

    def jsonPayoutBalanceInquiry(self):
        return ({
            "accountNo": self.accountNo,
            "additionalInfo": self.additionalInfo
        })
class BuilderPayoutBalanceInquiry:
    def __init__(self):
        self.accountNo = None
        self.additionalInfo = None

    def setAccountNo(self, accountNo):
        self.accountNo = accountNo
        return self

    def setAdditionalInfo(self, additionalInfo):
        self.additionalInfo = additionalInfo
        return self
class BuildPayoutBalanceInquiry(BuilderPayoutBalanceInquiry):
    def build(self):
        return PayoutBalanceInquiry(
            self.accountNo,
            self.additionalInfo
        )

class PayoutCancel:
    def __init__(self,
                 originalPartnerReferenceNo,
                 originalReferenceNo,
                 merchantId):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.merchantId = merchantId

    def jsonPayoutCancel(self):
        return ({
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "merchantId": self.merchantId
        })
class BuilderPayoutCancel:
    def __init__(self):
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.merchantId = None

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self
class BuildPayoutCancel(BuilderPayoutCancel):
    def build(self):
        return PayoutCancel(
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.merchantId
        )

class PayoutReject:
    def __init__(self,
                 originalPartnerReferenceNo,
                 originalReferenceNo,
                 merchantId):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        self.originalReferenceNo = originalReferenceNo
        self.merchantId = merchantId

    def jsonPayoutReject(self):
        return ({
            "originalPartnerReferenceNo": self.originalPartnerReferenceNo,
            "originalReferenceNo": self.originalReferenceNo,
            "merchantId": self.merchantId
        })
class BuilderPayoutReject:
    def __init__(self):
        self.originalPartnerReferenceNo = None
        self.originalReferenceNo = None
        self.merchantId = None

    def setOriginalPartnerReferenceNo(self, originalPartnerReferenceNo):
        self.originalPartnerReferenceNo = originalPartnerReferenceNo
        return self

    def setOriginalReferenceNo(self, originalReferenceNo):
        self.originalReferenceNo = originalReferenceNo
        return self

    def setMerchantId(self, merchantId):
        self.merchantId = merchantId
        return self
class BuildPayoutReject(BuilderPayoutReject):
    def build(self):
        return PayoutReject(
            self.originalPartnerReferenceNo,
            self.originalReferenceNo,
            self.merchantId
        )
