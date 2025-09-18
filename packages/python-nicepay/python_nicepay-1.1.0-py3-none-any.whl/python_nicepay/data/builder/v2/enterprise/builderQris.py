class Qris:
    def __init__(self,
                 payMethod,
                 mitraCd,
                 shopId,
                 paymentExpDt,
                 paymentExpTm,
                 amt):
        self.payMethod = payMethod
        self.mitraCd = mitraCd
        self.shopId = shopId
        self.paymentExpDt = paymentExpDt
        self.paymentExpTm = paymentExpTm
        self.amt = amt

    def jsonQris(self):
        return ({
            "payMethod": self.payMethod,
            "mitraCd": self.mitraCd,
            "shopId": self.shopId,
            "paymentExpDt": self.paymentExpDt,
            "paymentExpTm": self.paymentExpTm,
            "amt": self.amt
        })


class BuilderQris:
    def __init__(self):
        self.payMethod = None
        self.mitraCd = None
        self.shopId = None
        self.paymentExpDt = None
        self.paymentExpTm = None
        self.amt = None

    def setPayMethod(self, payMethod):
        self.payMethod = payMethod
        return self

    def setMitraCd(self, mitraCd):
        self.mitraCd = mitraCd
        return self

    def setShopId(self, shopId):
        self.shopId = shopId
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


class BuildQris(BuilderQris):
    def build(self):
        return Qris(
            self.payMethod,
            self.mitraCd,
            self.shopId,
            self.paymentExpDt,
            self.paymentExpTm,
            self.amt
        )
