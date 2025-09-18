class VirtualAccountV1:
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

    def jsonVirtualAccountV1(self):
        return ({
            "payMethod": self.payMethod,
            "bankCd": self.bankCd,
            "vacctValidDt": self.vacctValidDt,
            "vacctValidTm": self.vacctValidTm,
            "merFixAcctId": self.merFixAcctId,
            "amt": self.amt
        })


class BuilderVirtualAccountV1:
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


class BuildVirtualAccountV1(BuilderVirtualAccountV1):
    def build(self):
        return VirtualAccountV1(
            self.payMethod,
            self.bankCd,
            self.vacctValidDt,
            self.vacctValidTm,
            self.merFixAcctId,
            self.amt
        )