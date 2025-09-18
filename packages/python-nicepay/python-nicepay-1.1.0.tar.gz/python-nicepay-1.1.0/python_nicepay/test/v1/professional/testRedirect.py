from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.professional import builderRequest, builderCartData, builderSellers
from python_nicepay.data.builder.v2.professional.dataGenerator import DataGenerator
from python_nicepay.service.v1ProfessionalService import ServiceNicepayV1


class testRedirect:
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
        "sellerPhone": "08136368XXXX"
    }

    bodyCartData = (
        builderCartData.BuildCartData()
        .setCount("1")
        .setItem(itemCartData)
        .build()
    )

    bodySellers = (
        builderSellers.BuildSellers()
        .setSellerId("SEL123")
        .setSellerNm("Sellers")
        .setSellerEmail("sellers@example.com")
        .setSellerUrl("https://www.sellers.com")
        .setSellerAddress(itemSellersAddress)
        .build()
    )

    bodyRequest = (
        builderRequest.BuildRequest()
        .setPayMethod("00")
        .setInstmntType("1")
        .setInstmntMon("1")
        .setRecurrOpt("1")
        .setBankCd("CENA")
        .setMitraCd("")
        .setVacctValidDt("")
        .setVacctValidTm("")
        .setMerFixAcctId("")
        .setPayValidDt("")
        .setPayValidTm("")
        .setPaymentExpDt("")
        .setPaymentExpTm("")
        .setAmt(amt)
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepayV1.serviceRedirectV1(DataGenerator.getTransactionBody(bodyRequest.jsonRequest(),
                                                                               bodyCartData.jsonCartData(),
                                                                               bodySellers.jsonSellers()),environment)
