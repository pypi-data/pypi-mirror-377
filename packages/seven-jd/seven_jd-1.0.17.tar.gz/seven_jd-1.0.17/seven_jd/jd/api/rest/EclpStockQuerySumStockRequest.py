from seven_jd.jd.api.base import RestApi

class EclpStockQuerySumStockRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.warehouseNo = None
			self.goodsNo = None
			self.date = None
			self.isvGoodsNo = None

		def getapiname(self):
			return 'jingdong.eclp.stock.querySumStock'

			





