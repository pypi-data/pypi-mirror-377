class DirectDebit:
    def __init__(self,
                 payMethod,
                 mitraCd,
                 mRefNo,
                 amt):
        self.payMethod = payMethod
        self.mitraCd = mitraCd
        self.mRefNo = mRefNo
        self.amt = amt

    def jsonDirectDebit(self):
        return ({
            "payMethod": self.payMethod,
            "mitraCd": self.mitraCd,
            "mRefNo": self.mRefNo,
            "amt": self.amt
        })


class BuilderDirectDebit:
    def __init__(self):
        self.payMethod = None
        self.mitraCd = None
        self.mRefNo = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
        return self

    def setMRefNo(self, mRefNo):
        self.mRefNo = mRefNo
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildDirectDebit(BuilderDirectDebit):
    def build(self):
        return DirectDebit(
            self.payMethod,
            self.mitraCd,
            self.mRefNo,
            self.amt
        )
