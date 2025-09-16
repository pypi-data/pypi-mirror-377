from seven_jd.jd.api.base import RestApi

class EclpStockQueryVmiShopStockRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.goodsNos = None
			self.shopNos = None
			self.currentPage = None
			self.pageSize = None
			self.deptNo = None
			self.warehouseNo = None

		def getapiname(self):
			return 'jingdong.eclp.stock.queryVmiShopStock'

			





