from seven_jd.jd.api.base import RestApi

class LdopAlphaVendorBigshotQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.waybillCode = None
			self.providerId = None
			self.providerCode = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.vendor.bigshot.query'

			





