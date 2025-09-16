from seven_jd.jd.api.base import RestApi

class LdopAlphaProviderSignSuccessInfoGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.venderCode = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.provider.sign.success.info.get'

			





