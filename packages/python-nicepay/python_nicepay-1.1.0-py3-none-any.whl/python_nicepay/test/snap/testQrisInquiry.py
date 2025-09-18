from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderAccessToken, builderQris
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testQrisInquiry:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    additionalInfo = {

    }

    bodyQrisInquiry = (
        builderQris.BuildQrisInquiry()
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setExternalStoreId("NICEPAY")
        .setOriginalReferenceNo("_YOUR_TRANSACTION_ID")
        .setOriginalPartnerReferenceNo("OrdNo20250527112725")
        .setServiceCode("47")
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyQrisInquiry.jsonQrisInquiry(),
                                            ConstantsEndpoints.inquiryQris(),
                                            environment)
