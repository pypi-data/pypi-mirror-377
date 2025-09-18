class ConvenienceStore:
    def __init__(self,
                 payMethod,
                 mitraCd,
                 payValidDt,
                 payValidTm,
                 merFixAcctId,
                 amt):
        self.payMethod = payMethod
        self.mitraCd = mitraCd
        self.payValidDt = payValidDt
        self.payValidTm = payValidTm
        self.merFixAcctId = merFixAcctId
        self.amt = amt

    def jsonConvenienceStore(self):
        return ({
            "payMethod": self.payMethod,
            "mitraCd": self.mitraCd,
            "payValidDt": self.payValidDt,
            "payValidTm": self.payValidTm,
            "merFixAcctId": self.merFixAcctId,
            "amt": self.amt
        })


class BuilderConvenienceStore:
    def __init__(self):
        self.payMethod = None
        self.bankCd = None
        self.payValidDt = None
        self.payValidTm = None
        self.merFixAcctId = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
        return self

    def setPayValidDt(self, payValidDt):
        self.payValidDt = payValidDt
        return self

    def setPayValidTm(self, payValidTm):
        self.payValidTm = payValidTm
        return self

    def setMerFixAcctId(self, merFixAcctId):
        self.merFixAcctId = merFixAcctId
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildConvenienceStore(BuilderConvenienceStore):
    def build(self):
        return ConvenienceStore(
            self.payMethod,
            self.mitraCd,
            self.payValidDt,
            self.payValidTm,
            self.merFixAcctId,
            self.amt
        )
