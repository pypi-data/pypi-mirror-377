class Payout:
    def __init__(self,
                 accountNo,
                 benefNm,
                 benefPhone,
                 benefStatus,
                 benefType,
                 bankCd,
                 payoutMethod,
                 referenceNo,
                 reservedDt,
                 reservedTm,
                 amt,
                 description):
        self.accountNo = accountNo
        self.benefNm = benefNm
        self.benefPhone = benefPhone
        self.benefStatus = benefStatus
        self.benefType = benefType
        self.bankCd = bankCd
        self.payoutMethod = payoutMethod
        self.referenceNo = referenceNo
        self.reservedDt = reservedDt
        self.reservedTm = reservedTm
        self.amt = amt
        self.description = description

    def jsonPayout(self):
        return ({
            "accountNo": self.accountNo,
            "benefNm": self.benefNm,
            "benefPhone": self.benefPhone,
            "benefStatus": self.benefStatus,
            "benefType": self.benefType,
            "bankCd": self.bankCd,
            "payoutMethod": self.payoutMethod,
            "referenceNo": self.referenceNo,
            "reservedDt": self.reservedDt,
            "reservedTm": self.reservedTm,
            "amt": self.amt,
            "description": self.description
        })


class BuilderPayout:
    def __init__(self):
        self.accountNo = None
        self.benefNm = None
        self.benefPhone = None
        self.benefStatus = None
        self.benefType = None
        self.bankCd = None
        self.payoutMethod = None
        self.referenceNo = None
        self.reservedDt = None
        self.reservedTm = None
        self.amt = None
        self.description = None

    def setAccountNo(self, accountNo):
        self.accountNo = accountNo
        return self

    def setBenefNm(self, benefNm):
        self.benefNm = benefNm
        return self

    def setBenefPhone(self, benefPhone):
        self.benefPhone = benefPhone
        return self

    def setBenefStatus(self, benefStatus):
        self.benefStatus = benefStatus
        return self

    def setBenefType(self, benefType):
        self.benefType = benefType
        return self

    def setBankCd(self, bankCd):
        self.bankCd = bankCd
        return self

    def setPayoutMethod(self, payoutMethod):
        self.payoutMethod = payoutMethod
        return self

    def setReferenceNo(self, referenceNo):
        self.referenceNo = referenceNo
        return self

    def setReservedDt(self, reservedDt):
        self.reservedDt = reservedDt
        return self

    def setReservedTm(self, reservedTm):
        self.reservedTm = reservedTm
        return self

    def setAmt(self, amt):
        self.amt = amt
        return self

    def setDescription(self, description):
        self.description = description
        return self


class BuildPayout(BuilderPayout):
    def build(self):
        return Payout(
            self.accountNo,
            self.benefNm,
            self.benefPhone,
            self.benefStatus,
            self.benefType,
            self.bankCd,
            self.payoutMethod,
            self.referenceNo,
            self.reservedDt,
            self.reservedTm,
            self.amt,
            self.description
        )


class PayoutApprove:
    def __init__(self,
                 tXid):
        self.tXid = tXid

    def jsonPayoutApprove(self):
        return ({
            "timeStamp": "",
            "iMid": "",
            "merchantToken": "",
            "tXid": self.tXid
        })


class BuilderPayoutApprove:
    def __init__(self):
        self.tXid = None

    def setTxid(self, tXid):
        self.tXid = tXid
        return self


class BuildPayoutApprove(BuilderPayoutApprove):
    def build(self):
        return PayoutApprove(
            self.tXid
        )


class PayoutInquiry:
    def __init__(self,
                 accountNo,
                 tXid):
        self.accountNo = accountNo
        self.tXid = tXid

    def jsonPayoutInquiry(self):
        return ({
            "accountNo": self.accountNo,
            "tXid": self.tXid
        })


class BuilderPayoutInquiry:
    def __init__(self):
        self.accountNo = None
        self.tXid = None

    def setAccountNo(self, accountNo):
        self.accountNo = accountNo
        return self

    def setTxid(self, tXid):
        self.tXid = tXid
        return self


class BuildPayoutInquiry(BuilderPayoutInquiry):
    def build(self):
        return PayoutInquiry(
            self.accountNo,
            self.tXid
        )


class PayoutReject:
    def __init__(self,
                 tXid):
        self.tXid = tXid

    def jsonPayoutReject(self):
        return ({
            "tXid": self.tXid
        })


class BuilderPayoutReject:
    def __init__(self):
        self.tXid = None

    def setTxid(self, tXid):
        self.tXid = tXid
        return self


class BuildPayoutReject(BuilderPayoutReject):
    def build(self):
        return PayoutReject(
            self.tXid
        )


class PayoutCancel:
    def __init__(self,
                 tXid):
        self.tXid = tXid

    def jsonPayoutCancel(self):
        return ({
            "tXid": self.tXid
        })


class BuilderPayoutCancel:
    def __init__(self):
        self.tXid = None

    def setTxid(self, tXid):
        self.tXid = tXid
        return self


class BuildPayoutCancel(BuilderPayoutCancel):
    def build(self):
        return PayoutCancel(
            self.tXid
        )


