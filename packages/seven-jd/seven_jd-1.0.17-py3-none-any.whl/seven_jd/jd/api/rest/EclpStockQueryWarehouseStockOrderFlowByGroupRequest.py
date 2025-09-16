from seven_jd.jd.api.base import RestApi

class EclpStockQueryWarehouseStockOrderFlowByGroupRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.startDate = None
			self.endDate = None
			self.deptNo = None
			self.warehouseNo = None
			self.goodsNo = None
			self.isvGoodsNo = None
			self.orderType = None
			self.bizType = None

		def getapiname(self):
			return 'jingdong.eclp.stock.queryWarehouseStockOrderFlowByGroup'

			





