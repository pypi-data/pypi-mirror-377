from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderAccessToken, builderDirectDebit
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

class testDirectDebitInquiry:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    amount = {
        "value": "1.00",
        "currency": "IDR"
    }

    additionalInfo = {}

    bodyDirectDebitInquiry = (
        builderDirectDebit.BuildDirectDebitInquiry()
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setSubMerchantId("")
        .setOriginalPartnerReferenceNo("OrdNo20250807095315")
        .setOriginalReferenceNo("_YOUR_TRANSACTION_ID")
        .setServiceCode("54")
        .setTransactionDate(timestamp)
        .setAmount(amount)
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyDirectDebitInquiry.jsonDirectDebitInquiry(),
                                            ConstantsEndpoints.inquiryDirectDebit(),
                                            environment)
