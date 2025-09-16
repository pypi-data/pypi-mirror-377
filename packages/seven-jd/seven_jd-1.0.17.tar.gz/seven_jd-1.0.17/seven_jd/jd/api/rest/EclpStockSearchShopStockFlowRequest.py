from seven_jd.jd.api.base import RestApi

class EclpStockSearchShopStockFlowRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.requestId = None
			self.deptNo = None
			self.shopNo = None
			self.warehouseNo = None
			self.goodsNo = None
			self.startDate = None
			self.endDate = None
			self.pageNumber = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.eclp.stock.searchShopStockFlow'

			





