from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderVirtualAccount
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testVAFixedOpenUpdate:
    bodyVAFixedOpenUpdate = (
        builderVirtualAccount.BuildVAFixedOpenCustomerUpdate()
        .setCustomerId("32270522")
        .setCustomerNm("NEW_NAME")
        .setUpdateType("3")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.serviceVAFixedOpenUpdate(DataGenerator
                                                       .getVAFixedOpenUpdate(bodyVAFixedOpenUpdate
                                                                             .jsonVAFixedOpenCustomerUpdate()),environment)
