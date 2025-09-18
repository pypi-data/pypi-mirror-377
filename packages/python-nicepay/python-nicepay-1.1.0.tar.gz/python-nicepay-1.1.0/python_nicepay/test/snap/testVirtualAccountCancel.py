from python_nicepay.data.builder.snap import builderAccessToken, builderVirtualAccount
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()

class testVirtualAccountCancel:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    totalAmount = {"value": "10000.00",
                   "currency": "IDR"
                   }

    additionalInfo = {
            "tXidVA": "_YOUR_TRANSACTION_ID",
            "totalAmount": totalAmount,
            "cancelMessage": "Cancel Virtual Account"
                      }

    bodyCancelVA = (
        builderVirtualAccount.BuildCancelVA()
        .setPartnerServiceId("7001400002")
        .setCustomerNo("014647")
        .setVirtualAccountNo("7001400002014647")
        .setTrxId("NICEPAY123")
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyCancelVA.jsonVACancel(),
                                            ConstantsEndpoints.cancelVA(),
                                            environment,
                                            "DELETE")