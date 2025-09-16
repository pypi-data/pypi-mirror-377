from seven_jd.jd.api.base import RestApi

class LdopAlphaProviderStockIncreaseRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.operatorCode = None
			self.vendorCode = None
			self.vendorName = None
			self.providerId = None
			self.providerCode = None
			self.providerName = None
			self.branchCode = None
			self.branchName = None
			self.amount = None
			self.operatorTime = None
			self.operatorName = None
			self.state = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.provider.stock.increase'

			





