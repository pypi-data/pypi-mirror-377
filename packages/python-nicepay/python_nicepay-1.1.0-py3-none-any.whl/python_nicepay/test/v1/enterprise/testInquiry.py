from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v1.enterprise.dataGenerator import DataGeneratorV1
from python_nicepay.data.builder.v1.enterprise import builderInquiry
from python_nicepay.service.v1EnterpriseService import ServiceNicepayV1


class testInquiry:
    bodyInquiry = (
        builderInquiry.BuildInquiryV1()
        .setTxid("_YOUR_TRANSACTION_ID")
        .setReferenceNo("Nice20250814163220")
        .setAmt("10000")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())


    response = ServiceNicepayV1.serviceInquiryV1(DataGeneratorV1.getInquiryBodyV1(bodyInquiry.jsonInquiryV1()), environment)
