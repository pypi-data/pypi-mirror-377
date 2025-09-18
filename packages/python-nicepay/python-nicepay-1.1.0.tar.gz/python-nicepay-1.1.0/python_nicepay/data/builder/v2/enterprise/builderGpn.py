class Gpn:
    def __init__(self,
                 payMethod,
                 amt):
        self.payMethod = payMethod
        self.amt = amt

    def jsonGpn(self):
        return ({
            "payMethod": self.payMethod,
            "amt": self.amt
        })


class BuilderGpn:
    def __init__(self):
        self.payMethod = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildGpn(BuilderGpn):
    def build(self):
        return Gpn(
            self.payMethod,
            self.amt
        )
