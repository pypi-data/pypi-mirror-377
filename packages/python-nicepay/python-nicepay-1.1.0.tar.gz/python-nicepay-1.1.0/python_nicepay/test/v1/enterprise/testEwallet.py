from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v2.enterprise import builderCartData
from python_nicepay.data.builder.v1.enterprise import builderEwallet
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1

class testEwallet:

    amt = 1000
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
        builderEwallet.BuildEwalletV1()
        .setPayMethod(ConstantsGeneral.getPayMethodEWallet())
        .setMitraCd("DANA")
        .setUserIp(ConstantsGeneral.getUserIp())
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceEwalletRequestV1(DataGeneratorV1.getTransactionBodyV1(bodyEwallet.jsonEwalletV1(),
                                                                              bodyCartData.jsonCartData()), environment)
