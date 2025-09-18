from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v2.enterprise import builderCartData
from python_nicepay.data.builder.v1.enterprise import builderConvenienceStore
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1


class testConvenienceStore:
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

    bodyConvenienceStore = (
        builderConvenienceStore.BuildConvenienceStoreV1()
        .setPayMethod(ConstantsGeneral.getPayMethodConvenienceStore())
        .setMitraCd("INDO")
        .setPayValidDt("")
        .setPayValidTm("")
        .setMerFixAcctId("")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceRequestV1(DataGeneratorV1.getTransactionBodyV1(bodyConvenienceStore.jsonConvenienceStoreV1(),
                                                                              bodyCartData.jsonCartData()), environment)
