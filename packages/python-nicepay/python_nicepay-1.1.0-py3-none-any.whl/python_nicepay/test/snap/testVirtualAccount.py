from python_nicepay.data.builder.snap import builderAccessToken, builderVirtualAccount
from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment


log = Log()



class testVirtualAccount:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    totalAmount = {"value": "10000.00",
                   "currency": "IDR"
                   }

    additionalInfo = {"bankCd": "BMRI",
                      "goodsNm": "Merchant Goods 1",
                      "dbProcessUrl": "_YOUR_DB_PROCESS_URL_YOUR_DB_PROCESS_URL",
                      "vacctValidDt": "",
                      "vacctValidTm": "",
                      "msId": "",
                      "msFee": "",
                      "msFeeType": "",
                      "mbFee": "",
                      "mbFeeType": ""
                      }

    bodyCreateVA = (
        builderVirtualAccount.BuildCreateVA()
        .setPartnerServiceId("_YOUR_PREFIX_NO")
        .setCustomerNo("")
        .setVirtualAccountNo("")
        .setVirtualAccountName("TESTING DEV")
        .setTrxId("NICEPAY123")
        .setTotalAmount(totalAmount)
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyCreateVA.jsonVACreate(),
                                            ConstantsEndpoints.createVA(),
                                            environment)
