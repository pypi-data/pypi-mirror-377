from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderPayloan, builderCartData, builderSellers
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay

class testPayloan:
    amt = 10000
    itemCartData = {
        "goods_id": "GOODS001",
        "goods_name": "iPhone13ProMax",
        "goods_detail": "1TB-White",
        "goods_amt": amt,
        "goods_quantity": "1",
        "goods_type": "others",
        "goods_url": "https://cdn.eraspace.com/pub/media/catalog/product/i/p/iphone_13_pro_max_silver_1_5.jpg",
        "goods_sellers_id": "SEL123",
        "goods_sellers_name": "Sellers"
    }

    itemSellersAddress = {
        "sellerNm": "SEL123",
        "sellerLastNm": "One",
        "sellerAddr": "Jln.Jend.Sudirman",
        "sellerCity": "Central Jakarta",
        "sellerPostCd": "10202",
        "sellerCountry": "Indonesia",
        "sellerPhone": "08123456789"
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodySeller = (
        builderSellers.BuildSeller()
        .setSellerId("SEL123")
        .setSellerNm("Sellers")
        .setSellerEmail("sellers@example.com")
        .setSellerUrl("https://www.sellers.com")
        .setSellerAddress(itemSellersAddress)
        .build()
    )

    bodyPayloan = (
        builderPayloan.BuildPayloan()
        .setPayMethod(ConstantsGeneral.getPayMethodPayloan())
        .setInstmntType("1")
        .setInstmntMon("1")
        .setMitraCd("KDVI")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceRequest(DataGenerator.getPayloanBody(bodyPayloan.jsonPayloan(),
                                                                          bodyCartData.jsonCartData(),
                                                                          bodySeller.jsonSellers()), environment)
