from python_nicepay.data.builder import builderEnvironment
from python_nicepay.data.builder.v2.enterprise import builderPayout
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testPayoutCancel:
    bodyPayoutCancel = (
        builderPayout.BuildPayoutCancel()
        .setTxid("_YOUR_TRANSACTION_ID")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    response = ServiceNicepay.servicePayoutCancel(DataGenerator.
                                                  getPayoutCancel(bodyPayoutCancel.
                                                jsonPayoutCancel()), environment)
