from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderPayout, builderAccessToken
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testPayout:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    amount = {
        "value": "10001.00",
        "currency": "IDR"
    }

    bodyPayout = (
        builderPayout.BuildPayout()
        .setPartnerReferenceNo("OrdNo" + timestamp)
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setMsId("")
        .setBeneficiaryAccountNo("5930696651")
        .setBeneficiaryName("John Doe")
        .setBeneficiaryPhone("08123456789")
        .setBeneficiaryCustomerResidence("1")
        .setBeneficiaryCustomerType("1")
        .setBeneficiaryPostalCode("10200")
        .setBeneficiaryBankCode("CENA")
        .setBeneficiaryPOE("South Jakarta")
        .setBeneficiaryDOE("220101")
        .setBeneficiaryCoNo("12345JP")
        .setBeneficiaryAddress("Jln. Raya Kasablanka Kav.88")
        .setBeneficiaryAuthPhoneNumber("081623516151725XXX")
        .setBeneficiaryMerCategory("01")
        .setBeneficiaryCoMgmtName("John Doe")
        .setBeneficiaryCoShName("")
        .setPayoutMethod("1")
        .setReservedDt("")
        .setReservedTm("")
        .setDeliveryId("")
        .setDeliveryNm("Merchant's Name")
        .setAmount(amount)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyPayout.jsonPayout(),
                                            ConstantsEndpoints.payout(),
                                            environment)
