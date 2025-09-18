from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderAccessToken, builderDirectDebit
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log
from python_nicepay.data.builder import builderEnvironment

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testDirectDebit:

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

    urlParam = [
        {
            "url": "_YOUR_DB_PROCESS_URL",
            "type": "PAY_NOTIFY",
            "isDeeplink": "Y"
        },
        {
            "url": "https://www.nicepay.co.id/IONPAY_CLIENT/paymentResult.jsp",
            "type": "PAY_RETURN",
            "isDeeplink": "Y"
        }
    ]

    additionalInfo = {
        "mitraCd": "DANA",
        "goodsNm": "Merchant Goods 1",
        "billingNm": "Testin Dev",
        "billingPhone": "628136368XXXX",
        "cartData": "{\"count\":\"2\",\"item\":[{\"img_url\":\"http://img.aaa.com/ima1.jpg\",\"goods_name\":\"Item 1 Name\",\"goods_detail\":\"Item 1 Detail\",\"goods_amt\":\"0.00\",\"goods_quantity\":\"1\"},{\"img_url\":\"http://img.aaa.com/ima2.jpg\",\"goods_name\":\"Item 2 Name\",\"goods_detail\":\"Item 2 Detail\",\"goods_amt\":\"1.00\",\"goods_quantity\":\"1\"}]}",
        "dbProcessUrl": "_YOUR_DB_PROCESS_URL",
        "callBackUrl": "https://dev.nicepay.co.id/IONPAY_CLIENT/paymentResult.jsp",
        "msId": ""
    }

    bodyDirectDebit = (
        builderDirectDebit.BuildDirectDebit()
        .setPartnerReferenceNo("OrdNo" + timestamp)
        .setMerchantId("_YOUR_CLIENT_KEY")
        .setSubMerchantId("")
        .setExternalStoreId("")
        .setValidUpTo("")
        .setValidUpTo("")
        .setPointOfInitiation("Mobile App")
        .setAmount(amount)
        .setUrlParam(urlParam)
        .setAdditionalInfo(additionalInfo)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyDirectDebit.jsonDirectDebit(),
                                            ConstantsEndpoints.directDebit(),
                                            environment)
