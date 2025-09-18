from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderDirectDebit, builderCartData
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testDirectDebit:
    amt = 10000
    itemCartData = {
        "img_url": "https://cdn.eraspace.com/pub/media/catalog/product/i/p/iphone_13_pro_max_silver_1_5.jpg",
        "goods_name": "iPhone13ProMax",
        "goods_detail": "1TB-White",
        "goods_amt": amt
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodyDirectDebit = (
        builderDirectDebit.BuildDirectDebit()
        .setPayMethod(ConstantsGeneral.getPayMethodDirectDebit())
        .setMitraCd("JENC")
        .setMRefNo("")
        .setAmt(amt)
        .build()

    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceRequest(DataGenerator.getTransactionBody(bodyDirectDebit.jsonDirectDebit(),
                                                                              bodyCartData.jsonCartData()), environment)
