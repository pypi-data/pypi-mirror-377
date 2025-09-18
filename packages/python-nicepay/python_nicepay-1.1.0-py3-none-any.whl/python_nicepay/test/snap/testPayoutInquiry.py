from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderPayout, builderAccessToken
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testPayoutInquiry:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    bodyPayoutInquiry = (
        builderPayout.BuildPayoutInquiry()
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setOriginalPartnerReferenceNo("OrdNo20241114015744")
        .setOriginalReferenceNo("_YOUR_TRANSACTION_ID")
        .setBeneficiaryAccountNo("5345000060")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyPayoutInquiry.jsonPayoutInquiry(),
                                            ConstantsEndpoints.inquiryPayout(),
                                            environment)
