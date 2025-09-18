from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderPayout, builderAccessToken
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testPayoutBalanceInquiry:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    additionalInfo = {
        "msId": ""
    }

    bodyPayoutApprove = (
        builderPayout.BuildPayoutBalanceInquiry()
        .setAccountNo("")
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(True)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyPayoutApprove.jsonPayoutBalanceInquiry(),
                                            ConstantsEndpoints.balanceInquiryPayout(),
                                            environment)
