from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderVirtualAccount
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testVAFixedOpenCustInq:
    bodyVAFixedOpenInq = (
        builderVirtualAccount.BuildVAFixedOpenCustInq()
        .setCustomerId("123458")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceVAFixedOpenCustInq(DataGenerator.getVAFixedOpenCustInq(bodyVAFixedOpenInq
                                                                                            .jsonVAFixedOpenCustInq()),environment)
