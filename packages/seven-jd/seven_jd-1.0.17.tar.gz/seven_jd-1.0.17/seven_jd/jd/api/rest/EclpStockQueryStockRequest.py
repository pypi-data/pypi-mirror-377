from seven_jd.jd.api.base import RestApi

class EclpStockQueryStockRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.warehouseNo = None
			self.stockStatus = None
			self.stockType = None
			self.goodsNo = None
			self.currentPage = None
			self.pageSize = None
			self.returnZeroStock = None
			self.returnIsvLotattrs = None
			self.goodsLevel = None
			self.isvSku = None
			self.sellerGoodsSign = None

		def getapiname(self):
			return 'jingdong.eclp.stock.queryStock'

			





