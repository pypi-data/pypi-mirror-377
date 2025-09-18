class Payloan:
    def __init__(self,
                 payMethod,
                 instmntType,
                 instmntMon,
                 mitraCd,
                 amt):
        self.payMethod = payMethod
        self.instmntType = instmntType
        self.instmntMon = instmntMon
        self.mitraCd = mitraCd
        self.amt = amt

    def jsonPayloan(self):
        return ({
            "payMethod": self.payMethod,
            "instmntType": self.instmntType,
            "instmntMon": self.instmntMon,
            "mitraCd": self.mitraCd,
            "amt": self.amt
        })


class BuilderPayloan:
    def __init__(self):
        self.payMethod = None
        self.instmntType = None
        self.instmntMon = None
        self.mitraCd = None
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

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildPayloan(BuilderPayloan):
    def build(self):
        return Payloan(
            self.payMethod,
            self.instmntType,
            self.instmntMon,
            self.mitraCd,
            self.amt
        )
