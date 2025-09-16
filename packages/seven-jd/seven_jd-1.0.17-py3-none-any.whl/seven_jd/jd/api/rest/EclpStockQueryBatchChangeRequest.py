from seven_jd.jd.api.base import RestApi

class EclpStockQueryBatchChangeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.allocativeCenterNo = None
			self.warehouseNo = None
			self.batchAttrChangeNo = None
			self.startTime = None
			self.endTime = None
			self.startPage = None
			self.onePageNum = None

		def getapiname(self):
			return 'jingdong.eclp.stock.queryBatchChange'

			





