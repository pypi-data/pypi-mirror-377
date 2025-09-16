from seven_jd.jd.api.base import RestApi

class ApplyAddMerchantsAddRequest(RestApi):
    def __init__(self, domain='gw.api.360buy.com', port=80):
        """
			"""
        RestApi.__init__(self, domain, port)
        self.data = None
        self.merchantCode = None

    def getapiname(self):
        return 'jingdong.applyAddMerchants.add'
