from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.professional import builderInquiry
from python_nicepay.data.builder.v2.professional.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testInquiry:
    bodyInquiry = (
        builderInquiry.BuildInquiry()
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("OrdNo20241109190350")
        .setAmt("10000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceInquiry(DataGenerator.getInquiryBody(bodyInquiry.jsonInquiry()),environment)
