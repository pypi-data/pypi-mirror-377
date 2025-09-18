class Ewallet:
    def __init__(self,
                 payMethod,
                 mitraCd,
                 userIp,
                 amt):
        self.payMethod = payMethod
        self.mitraCd = mitraCd
        self.userIp = userIp
        self.amt = amt

    def jsonEwallet(self):
        return ({
            "payMethod": self.payMethod,
            "mitraCd": self.mitraCd,
            "userIP": self.userIp,
            "amt": self.amt
        })


class BuilderEwallet:
    def __init__(self):
        self.payMethod = None
        self.mitraCd = None
        self.userIp = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
        return self

    def setUserIp(self, userIp):
        self.userIp = userIp
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildEwallet(BuilderEwallet):
    def build(self):
        return Ewallet(
            self.payMethod,
            self.mitraCd,
            self.userIp,
            self.amt
        )
