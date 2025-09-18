from python_nicepay.data.builder.snap import builderAccessToken
from python_nicepay.service.snapService import SnapService
from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder import builderEnvironment

class testAccessToken:
    # Case if merchant using different config with the constant
    # clientKey = "_CLIENT_KEY_MERCHANT"
    # clientSecret = "_CLIENT_SECRET_MERCHANT"
    # privateKey= "_PRIVATE_KEY_MERCHANT"
    #
    # ConstantsGeneral.setSnapConfiguration(clientKey, clientSecret, privateKey)

    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    environment = (builderEnvironment.BuildEnvironment()
                   .isCloud(False)
                   .isProduction(False)
                   .build())

    result = SnapService.serviceOAUTH(bodyCreateToken.jsonAccessToken(), environment)
