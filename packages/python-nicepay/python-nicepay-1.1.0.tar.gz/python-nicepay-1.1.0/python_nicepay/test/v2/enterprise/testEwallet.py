from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderCartData, builderEwallet
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay

class testEwallet:
    # Set the internal merchant configuration
    # imid = "_YOUR_I_MID"
    # merchantKey = "_YOUR_MERCHANT_KEY"
    # callbackUrl = "https://dev.nicepay.co.id/IONPAY_CLIENT/paymentResult.jsp"
    # dbProcessUrl = "_YOUR_DB_PROCESS_URL"
    # billingPhone = "0812345XXXX"
    # ConstantsGeneral.setNonSnapConfiguration(imid, merchantKey, dbProcessUrl, callbackUrl)
    # ConstantsGeneral.setBillingPhone(billingPhone)

    amt = 1
    itemCartData = {
        "img_url": "https://cdn.eraspace.com/pub/media/catalog/product/i/p/iphone_13_pro_max_silver_1_5.jpg",
        "goods_name": "iPhone13ProMax",
        "goods_detail": "1TB-White",
        "goods_amt": amt,
        "goods_quantity": "1"
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodyEwallet = (
        builderEwallet.BuildEwallet()
        .setPayMethod(ConstantsGeneral.getPayMethodEWallet())
        .setMitraCd("LINK")
        .setUserIp(ConstantsGeneral.getUserIp())
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceRequest(DataGenerator.getTransactionBody(bodyEwallet.jsonEwallet(),
                                                                              bodyCartData.jsonCartData()), environment)
