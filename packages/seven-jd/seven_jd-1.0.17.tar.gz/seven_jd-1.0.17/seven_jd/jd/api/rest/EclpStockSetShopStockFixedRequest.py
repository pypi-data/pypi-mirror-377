from seven_jd.jd.api.base import RestApi

class EclpStockSetShopStockFixedRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.requestId = None
			self.deptNo = None
			self.shopNo = None
			self.warehouseNo = None
			self.stockNum = None
			self.goodsNo = None
			self.shopType = None
			self.opUser = None

		def getapiname(self):
			return 'jingdong.eclp.stock.setShopStockFixed'

			





