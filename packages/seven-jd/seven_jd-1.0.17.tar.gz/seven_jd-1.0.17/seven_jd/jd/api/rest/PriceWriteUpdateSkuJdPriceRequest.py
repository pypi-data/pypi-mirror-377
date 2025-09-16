from seven_jd.jd.api.base import RestApi

class PriceWriteUpdateSkuJdPriceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.jdPrice = None
			self.skuId = None

		def getapiname(self):
			return 'jingdong.price.write.updateSkuJdPrice'

			





