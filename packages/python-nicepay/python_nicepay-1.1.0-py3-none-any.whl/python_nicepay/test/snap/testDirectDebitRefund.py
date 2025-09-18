from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderAccessToken, builderDirectDebit
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testDirectDebitRefund:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    refundAmount = {
        "value": "1.00",
        "currency": "IDR"
    }

    additionalInfo = {
        "refundType": "1"
    }

    bodyDirectDebitRefund = (
        builderDirectDebit.BuildDirectDebitRefund()
        .setPartnerRefundNo("RefundNo" + timestamp)
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setSubMerchantId("")
        .setOriginalPartnerReferenceNo("OrdNo20250812171542")
        .setOriginalReferenceNo("_YOUR_CLIENT_KEY")
        .setExternalStoreId("NICEPAY")
        .setReason("Testing Refund OVOE SNAP")
        .setRefundAmount(refundAmount)
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyDirectDebitRefund.jsonDirectDebitRefund(),
                                            ConstantsEndpoints.refundDirectDebit(),
                                            environment)
