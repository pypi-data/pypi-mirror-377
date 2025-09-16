from seven_jd.jd.api.base import RestApi

class EclpStockSearchShopStockRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.requestId = None
			self.deptNo = None
			self.shopNo = None
			self.warehouseNo = None
			self.goodsNo = None
			self.pageSize = None
			self.pageNumber = None

		def getapiname(self):
			return 'jingdong.eclp.stock.searchShopStock'

			





