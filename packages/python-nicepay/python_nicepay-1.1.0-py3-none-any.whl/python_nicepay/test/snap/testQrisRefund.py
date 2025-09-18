from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderAccessToken, builderQris
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
class testQrisRefund:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    refundAmount = {
        "value": "10000.00",
        "currency": "IDR"
    }

    additionalInfo = {
        "cancelType": "1"
    }

    bodyQrisInquiry = (
        builderQris.BuildQrisRefund()
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setExternalStoreId("NICEPAY")
        .setOriginalReferenceNo("_YOUR_TRANSACTION_ID")
        .setOriginalPartnerReferenceNo("OrdNo20250527120034")
        .setPartnerRefundNo("51")
        .setRefundAmount(refundAmount)
        .setReason("Test Refund QRIS SNAP")
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyQrisInquiry.jsonQrisRefund(),
                                            ConstantsEndpoints.refundQris(),
                                            environment)
    