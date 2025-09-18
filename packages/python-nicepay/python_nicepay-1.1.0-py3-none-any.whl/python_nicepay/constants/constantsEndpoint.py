from tkinter.messagebox import RETRY


class ConstantsEndpoints:
    # SNAP
    _ACCESS_TOKEN = "/v1.0/access-token/b2b"
    _CREATE_VA = "/api/v1.0/transfer-va/create-va"
    _INQUIRY_VA = "/api/v1.0/transfer-va/status"
    _CANCEL_VA = "/api/v1.0/transfer-va/delete-va"
    _DIRECT_DEBIT = "/api/v1.0/debit/payment-host-to-host"
    _INQUIRY_DIRECT_DEBIT = "/api/v1.0/debit/status"
    _REFUND_DIRECT_DEBIT = "/api/v1.0/debit/refund"
    _QRIS = "/api/v1.0/qr/qr-mpm-generate"
    _INQUIRY_QRIS = "/api/v1.0/qr/qr-mpm-query"
    _REFUND_QRIS = "/api/v1.0/qr/qr-mpm-refund"
    _PAYOUT = "/api/v1.0/transfer/registration"
    _APPROVE_PAYOUT = "/api/v1.0/transfer/approve"
    _INQUIRY_PAYOUT = "/api/v1.0/transfer/inquiry"
    _CANCEL_PAYOUT = "/api/v1.0/transfer/cancel"
    _REJECT_PAYOUT = "/api/v1.0/transfer/reject"
    _BALANCE_INQUIRY_PAYOUT = "/api/v1.0/balance-inquiry"

    # V2-ENTERPRISE
    _REGISTRATION = "/direct/v2/registration"
    _PAYMENT = "/direct/v2/payment"
    _INQUIRY = "/direct/v2/inquiry"
    _CANCEL = "/direct/v2/cancel"
    _VA_FIXED_OPEN_REGISTRATION = "/api/vacctCustomerRegist.do"
    _VA_FIXED_OPEN_CUSTOMER_INQUIRY = "/api/vacctCustomerInquiry.do"
    _VA_FIXED_OPEN_DEPOSIT_INQUIRY = "/api/vacctInquiry.do"
    _VA_FIXED_OPEN_CUSTOMER_UPDATE = "/api/vacctCustomerUpdate.do"
    _PAYOUT_REGISTRATION = "/api/direct/v2/requestPayout"
    _PAYOUT_APPROVE = "/api/direct/v2/approvePayout"
    _PAYOUT_INQUIRY = "/api/direct/v2/inquiryPayout"
    _PAYOUT_REJECT = "/api/direct/v2/rejectPayout"
    _PAYOUT_CANCEL = "/api/direct/v2/cancelPayout"
    _PAYOUT_BALANCE_INQUIRY = "/api/direct/v2/balanceInquiry"
    _PAYOUT_TRANSACTION_HISTORY_INQUIRY = "/direct/v2/historyInquiry"
    _PAYOUT_RECURRING_REQUEST = "/api/direct/v2/recurringRequest"
    _PAYOUT_SELLER_BALANCE_TRANSFER = "/api/direct/v2/sellerBalanceTransfer"
    _PAYOUT_MERCHANT_BALANCE_TRANSFER = "/api/direct/v2/merchantBalanceTransfer"
    _PAYOUT_LIST_INQUIRY = "/direct/v2/listInquiry"

    # V2-PROFESSIONAL
    _REGISTRATION_REDIRECT = "/redirect/v2/registration"
    _PAYMENT_REDIRECT = "/redirect/v2/payment"

    # V1-ENTERPRISE
    _REQUEST_ONE_PASS_TOKEN = "/api/onePassToken.do"
    _REQUEST_3DS_TOKEN = "/api/secureVeRequest.do" #PAYMENT = 1 3DS
    _REQUEST_MIGS_TOKEN = "/api/migsRequest.do" #PAYMENT = 3 MIGS
    _REGISTRATION_V1 = "/api/onePass.do"
    _REGISTRATION_V1_EWALLET = "/api/ewalletTrans.do"
    _INQUIRY_V1 = "/api/onePassStatus.do"
    _CANCEL_V1 = "/api/onePassAllCancel.do"

    # V1-PROFESSIONAL
    _REGISTRATION_REDIRECT_V1 = "/api/orderRegist.do"
    _REDIRECT_INQUIRY_V1 = "/api/orderInquiry.do"


    #SNAP
    @staticmethod
    def accessToken():
        return ConstantsEndpoints._ACCESS_TOKEN

    @staticmethod
    def createVA():
        return ConstantsEndpoints._CREATE_VA

    @staticmethod
    def inquiryVA():
        return ConstantsEndpoints._INQUIRY_VA

    @staticmethod
    def cancelVA():
        return ConstantsEndpoints._CANCEL_VA

    @staticmethod
    def directDebit():
        return ConstantsEndpoints._DIRECT_DEBIT

    @staticmethod
    def inquiryDirectDebit():
        return ConstantsEndpoints._INQUIRY_DIRECT_DEBIT

    @staticmethod
    def refundDirectDebit():
        return ConstantsEndpoints._REFUND_DIRECT_DEBIT

    @staticmethod
    def qris():
        return ConstantsEndpoints._QRIS

    @staticmethod
    def inquiryQris():
        return ConstantsEndpoints._INQUIRY_QRIS

    @staticmethod
    def refundQris():
        return ConstantsEndpoints._REFUND_QRIS

    @staticmethod
    def payout():
        return ConstantsEndpoints._PAYOUT

    @staticmethod
    def inquiryPayout():
        return ConstantsEndpoints._INQUIRY_PAYOUT

    @staticmethod
    def approvePayout():
        return ConstantsEndpoints._APPROVE_PAYOUT

    @staticmethod
    def cancelPayout():
        return ConstantsEndpoints._CANCEL_PAYOUT

    @staticmethod
    def rejectPayout():
        return ConstantsEndpoints._REJECT_PAYOUT

    @staticmethod
    def balanceInquiryPayout():
        return ConstantsEndpoints._BALANCE_INQUIRY_PAYOUT

    # V2-ENTERPRISE
    @staticmethod
    def registration():
        return ConstantsEndpoints._REGISTRATION

    @staticmethod
    def payment():
        return ConstantsEndpoints._PAYMENT

    @staticmethod
    def inquiry():
        return ConstantsEndpoints._INQUIRY

    @staticmethod
    def cancel():
        return ConstantsEndpoints._CANCEL

    @staticmethod
    def vaFixedOpenRegist():
        return ConstantsEndpoints._VA_FIXED_OPEN_REGISTRATION

    @staticmethod
    def vaFixedOpenCustInq():
        return ConstantsEndpoints._VA_FIXED_OPEN_CUSTOMER_INQUIRY

    @staticmethod
    def vaFixedOpenDepositInq():
        return ConstantsEndpoints._VA_FIXED_OPEN_DEPOSIT_INQUIRY

    @staticmethod
    def vaFixedOpenCustUpdate():
        return ConstantsEndpoints._VA_FIXED_OPEN_CUSTOMER_UPDATE

    @staticmethod
    def payoutRegistration():
        return ConstantsEndpoints._PAYOUT_REGISTRATION

    @staticmethod
    def payoutApprove():
        return ConstantsEndpoints._PAYOUT_APPROVE

    @staticmethod
    def payoutInquiry():
        return ConstantsEndpoints._PAYOUT_INQUIRY

    @staticmethod
    def payoutReject():
        return ConstantsEndpoints._PAYOUT_REJECT

    @staticmethod
    def payoutCancel():
        return ConstantsEndpoints._PAYOUT_CANCEL

    @staticmethod
    def payoutBalanceInq():
        return ConstantsEndpoints._PAYOUT_BALANCE_INQUIRY

    @staticmethod
    def payoutTransHistInq():
        return ConstantsEndpoints._PAYOUT_TRANSACTION_HISTORY_INQUIRY

    @staticmethod
    def payoutRecurringReq():
        return ConstantsEndpoints._PAYOUT_RECURRING_REQUEST

    @staticmethod
    def payoutSellerBalanceTransfer():
        return ConstantsEndpoints._PAYOUT_SELLER_BALANCE_TRANSFER

    @staticmethod
    def payoutMerchantBalanceTransfer():
        return ConstantsEndpoints._PAYOUT_MERCHANT_BALANCE_TRANSFER

    @staticmethod
    def payoutListInquiry():
        return ConstantsEndpoints._PAYOUT_LIST_INQUIRY

    # V2-PROFESSIONAL
    @staticmethod
    def registrationRedirect():
        return ConstantsEndpoints._REGISTRATION_REDIRECT

    @staticmethod
    def paymentRedirect():
        return ConstantsEndpoints._PAYMENT_REDIRECT


   # V1- ENTERPRISE
    @staticmethod
    def requestOnePassToken():
        return ConstantsEndpoints._REQUEST_ONE_PASS_TOKEN

    @staticmethod
    def request3DSToken():
        return ConstantsEndpoints._REQUEST_3DS_TOKEN

    @staticmethod
    def requestMigsToken():
        return ConstantsEndpoints._REQUEST_MIGS_TOKEN

    @staticmethod
    def requestRegistrationV1():
        return ConstantsEndpoints._REGISTRATION_V1

    @staticmethod
    def requestRegistrationV1Ewallet():
        return ConstantsEndpoints._REGISTRATION_V1_EWALLET

    @staticmethod
    def inquiryV1():
        return ConstantsEndpoints._INQUIRY_V1

    @staticmethod
    def cancelV1():
        return ConstantsEndpoints._CANCEL_V1

    @staticmethod
    def registrationRedirectV1():
        return ConstantsEndpoints._REGISTRATION_REDIRECT_V1

    @staticmethod
    def inquiryRedirectV1():
        return ConstantsEndpoints._REDIRECT_INQUIRY_V1
