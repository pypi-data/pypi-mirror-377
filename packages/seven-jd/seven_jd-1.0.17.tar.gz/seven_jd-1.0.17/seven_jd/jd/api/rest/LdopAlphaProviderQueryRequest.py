from seven_jd.jd.api.base import RestApi

class LdopAlphaProviderQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.providerState = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.provider.query'

			





