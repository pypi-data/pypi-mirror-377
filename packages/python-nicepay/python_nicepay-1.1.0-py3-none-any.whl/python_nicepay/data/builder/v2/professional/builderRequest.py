class Request:
    def __init__(self,
                 payMethod,
                 instmntType,
                 instmntMon,
                 recurrOpt,
                 bankCd,
                 mitraCd,
                 vacctValidDt,
                 vacctValidTm,
                 merFixAcctId,
                 payValidDt,
                 payValidTm,
                 paymentExpDt,
                 paymentExpTm,
                 amt):
        self.payMethod = payMethod
        self.instmntType = instmntType
        self.instmntMon = instmntMon
        self.recurrOpt = recurrOpt
        self.bankCd = bankCd
        self.mitraCd = mitraCd
        self.vacctValidDt = vacctValidDt
        self.vacctValidTm = vacctValidTm
        self.merFixAcctId = merFixAcctId
        self.payValidDt = payValidDt
        self.payValidTm = payValidTm
        self.paymentExpDt = paymentExpDt
        self.paymentExpTm = paymentExpTm
        self.amt = amt

    def jsonRequest(self):
        return ({
            "payMethod": self.payMethod,
            "instmntType": self.instmntType,
            "instmntMon": self.instmntMon,
            "recurrOpt": self.recurrOpt,
            "bankCd": self.bankCd,
            "mitraCd": self.mitraCd,
            "vacctValidDt": self.vacctValidDt,
            "vacctValidTm": self.vacctValidTm,
            "merFixAcctId": self.merFixAcctId,
            "payValidDt": self.payValidDt,
            "payValidTm": self.payValidTm,
            "paymentExpDt": self.paymentExpDt,
            "paymentExpTm": self.paymentExpTm,
            "amt": self.amt
        })

class BuilderRequest:
    def __init__(self):
        self.payMethod = None
        self.instmntType = None
        self.instmntMon = None
        self.recurrOpt = None
        self.bankCd = None
        self.mitraCd = None
        self.vacctValidDt = None
        self.vacctValidTm = None
        self.merFixAcctId = None
        self.payValidDt = None
        self.payValidTm = None
        self.paymentExpDt = None
        self.paymentExpTm = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setInstmntType(self, instmntType):
        self.instmntType = instmntType
        return self

    def setInstmntMon(self, instmntMon):
        self.instmntMon = instmntMon
        return self

    def setRecurrOpt(self, recurrOpt):
        self.recurrOpt = recurrOpt
        return self

    def setBankCd(self, bankCd):
        self.bankCd = bankCd
        return self

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
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

    def setPayValidDt(self, payValidDt):
        self.payValidDt = payValidDt
        return self

    def setPayValidTm(self, payValidTm):
        self.payValidTm = payValidTm
        return self

    def setPaymentExpDt(self, paymentExpDt):
        self.paymentExpDt = paymentExpDt
        return self

    def setPaymentExpTm(self, paymentExpTm):
        self.paymentExpTm = paymentExpTm
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self

class BuildRequest(BuilderRequest):
    def build(self):
        return Request(
            self.payMethod,
            self.instmntType,
            self.instmntMon,
            self.recurrOpt,
            self.bankCd,
            self.mitraCd,
            self.vacctValidDt,
            self.vacctValidTm,
            self.merFixAcctId,
            self.payValidDt,
            self.payValidTm,
            self.paymentExpDt,
            self.paymentExpTm,
            self.amt
        )
