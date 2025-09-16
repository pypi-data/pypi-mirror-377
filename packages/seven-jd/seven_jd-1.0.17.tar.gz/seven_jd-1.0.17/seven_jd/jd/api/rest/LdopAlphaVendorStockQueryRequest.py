from seven_jd.jd.api.base import RestApi

class LdopAlphaVendorStockQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.vendorCode = None
			self.providerId = None
			self.branchCode = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.vendor.stock.query'

			





