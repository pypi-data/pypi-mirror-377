from seven_jd.jd.api.base import RestApi

class LdopAlphaProviderStockQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.providerCode = None
			self.branchCode = None
			self.vendorCode = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.provider.stock.query'

			





