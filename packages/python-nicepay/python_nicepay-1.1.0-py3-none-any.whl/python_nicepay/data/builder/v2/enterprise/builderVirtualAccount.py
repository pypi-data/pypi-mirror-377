class VirtualAccount:
    def __init__(self,
                 payMethod,
                 bankCd,
                 vacctValidDt,
                 vacctValidTm,
                 merFixAcctId,
                 amt):
        self.payMethod = payMethod
        self.bankCd = bankCd
        self.vacctValidDt = vacctValidDt
        self.vacctValidTm = vacctValidTm
        self.merFixAcctId = merFixAcctId
        self.amt = amt

    def jsonVirtualAccount(self):
        return ({
            "payMethod": self.payMethod,
            "bankCd": self.bankCd,
            "vacctValidDt": self.vacctValidDt,
            "vacctValidTm": self.vacctValidTm,
            "merFixAcctId": self.merFixAcctId,
            "amt": self.amt
        })


class BuilderVirtualAccount:
    def __init__(self):
        self.payMethod = None
        self.bankCd = None
        self.vacctValidDt = None
        self.vacctValidTm = None
        self.merFixAcctId = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setBankCd(self, bankCd):
        self.bankCd = bankCd
        return self

    def setVacctValidDt(self, vacctValidDt):
        self.vacctValidDt = vacctValidDt
        return self

    def setVacctValidTm(self, vacctValidTm):
        self.vacctValidTm = vacctValidTm
        return self

    def setMerFixAcctId(self, merFixAcctId):
        self.merFixAcctId = merFixAcctId
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildVirtualAccount(BuilderVirtualAccount):
    def build(self):
        return VirtualAccount(
            self.payMethod,
            self.bankCd,
            self.vacctValidDt,
            self.vacctValidTm,
            self.merFixAcctId,
            self.amt
        )


# VIRTUAL ACCOUNT FIXED OPEN REGISTRATION
class VAFixedOpenReg:
    def __init__(self,
                 customerId,
                 customerNm):
        self.customerId = customerId
        self.customerNm = customerNm

    def jsonVAFixedOpenReg(self):
        return ({
            "customerId": self.customerId,
            "customerNm": self.customerNm
        })


class BuilderVAFixedOpenReg:
    def __init__(self):
        self.customerId = None
        self.customerNm = None

    def setCustomerId(self, customerId):
        self.customerId = customerId
        return self

    def setCustomerNm(self, customerNm):
        self.customerNm = customerNm
        return self


class BuildVAFixedOpenReg(BuilderVAFixedOpenReg):
    def build(self):
        return VAFixedOpenReg(
            self.customerId,
            self.customerNm
        )


# VIRTUAL ACCOUNT FIXED OPEN INQUIRY (CUSTOMER INQUIRY)
class VAFixedOpenCustInq:
    def __init__(self,
                 customerId):
        self.customerId = customerId

    def jsonVAFixedOpenCustInq(self):
        return ({
            "customerId": self.customerId
        })


class BuilderVAFixedOpenCustInq:
    def __init__(self):
        self.customerId = None

    def setCustomerId(self, customerId):
        self.customerId = customerId
        return self


class BuildVAFixedOpenCustInq(BuilderVAFixedOpenCustInq):
    def build(self):
        return VAFixedOpenCustInq(
            self.customerId
        )


# VIRTUAL ACCOUNT FIXED OPEN INQUIRY (DEPOSIT INQUIRY)
class VAFixedOpenDepositInquiry:
    def __init__(self,
                 vacctNo,
                 startDt,
                 endDt):
        self.vacctNo = vacctNo
        self.startDt = startDt
        self.endDt = endDt

    def jsonVAFixedOpenDepositInq(self):
        return ({
            "vacctNo": self.vacctNo,
            "startDt": self.startDt,
            "endDt": self.endDt
        })


class BuilderVAFixedOpenDepositInq:
    def __init__(self):
        self.vacctNo = None
        self.startDt = None
        self.endDt = None

    def setVacctNo(self, vacctNo):
        self.vacctNo = vacctNo
        return self

    def setStartDt(self, startDt):
        self.startDt = startDt
        return self

    def setEndDt(self, endDt):
        self.endDt = endDt
        return self


class BuildVAFixedOpenDepositInq(BuilderVAFixedOpenDepositInq):
    def build(self):
        return VAFixedOpenDepositInquiry(
            self.vacctNo,
            self.startDt,
            self.endDt
        )


# VIRTUAL ACCOUNT FIXED OPEN CUSTOMER UPDATE
class VAFixedOpenCustomerUpdate:
    def __init__(self,
                 customerId,
                 customerNm,
                 updateType):
        self.customerId = customerId
        self.customerNm = customerNm
        self.updateType = updateType

    def jsonVAFixedOpenCustomerUpdate(self):
        return ({
            "customerId": self.customerId,
            "customerNm": self.customerNm,
            "updateType": self.updateType
        })


class BuilderVAFixedOpenCustomerUpdate:
    def __init__(self):
        self.customerId = None
        self.customerNm = None
        self.updateType = None

    def setCustomerId(self, customerId):
        self.customerId = customerId
        return self

    def setCustomerNm(self, customerNm):
        self.customerNm = customerNm
        return self

    def setUpdateType(self, updateType):
        self.updateType = updateType
        return self


class BuildVAFixedOpenCustomerUpdate(BuilderVAFixedOpenCustomerUpdate):
    def build(self):
        return VAFixedOpenCustomerUpdate(
            self.customerId,
            self.customerNm,
            self.updateType
        )
