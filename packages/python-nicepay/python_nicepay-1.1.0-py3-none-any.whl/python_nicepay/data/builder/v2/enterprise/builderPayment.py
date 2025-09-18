class Payment:
    def __init__(self,
                 timestamp,
                 tXid,
                 referenceNo,
                 cashtag,
                 cardNo,
                 cardExpYymm,
                 cardCvv,
                 recurringToken,
                 preauthToken,
                 amt):
        self.timestamp = timestamp
        self.tXid = tXid
        self.referenceNo = referenceNo
        self.cashtag = cashtag
        self.cardNo = cardNo
        self.cardExpYymm = cardExpYymm
        self.cardCvv = cardCvv
        self.recurringToken = recurringToken
        self.preauthToken = preauthToken
        self.amt = amt

    def dataPayment(self):
        return ({
            "timeStamp": self.timestamp,
            "tXid": self.tXid,
            "referenceNo": self.referenceNo,
            "cashtag": self.cashtag,
            "cardNo": self.cardNo,
            "cardExpYymm": self.cardExpYymm,
            "cardCvv": self.cardCvv,
            "recurringToken": self.recurringToken,
            "preauthToken": self.preauthToken,
            "amt": self.amt
        })


class BuilderPayment:
    def __init__(self):
        self.timestamp = None
        self.tXid = None
        self.referenceNo = None
        self.cashtag = None
        self.cardNo = None
        self.cardExpYymm = None
        self.cardCvv = None
        self.recurringToken = None
        self.preauthToken = None
        self.amt = None

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
        return self

    def setTxid(self, tXid):
        self.tXid = tXid
        return self

    def setReferenceNo(self, referenceNo):
        self.referenceNo = referenceNo
        return self

    def setCashtag(self, cashtag):
        self.cashtag = cashtag
        return self

    def setCardNo(self, cardNo):
        self.cardNo = cardNo
        return self

    def setCardExpYymm(self, cardExpYymm):
        self.cardExpYymm = cardExpYymm
        return self

    def setCardCvv(self, cardCvv):
        self.cardCvv = cardCvv
        return self

    def setRecurringToken(self, recurringToken):
        self.recurringToken = recurringToken
        return self

    def setPreAuthToken(self, preauthToken):
        self.preauthToken = preauthToken
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self


class BuildPayment(BuilderPayment):
    def build(self):
        return Payment(
            self.timestamp,
            self.tXid,
            self.referenceNo,
            self.cashtag,
            self.cardNo,
            self.cardExpYymm,
            self.cardCvv,
            self.recurringToken,
            self.preauthToken,
            self.amt
        )
