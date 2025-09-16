from seven_jd.jd.api.base import RestApi

class EclpCheckstockQueryCheckStockProfitRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.checkStockNos = None
			self.pageNo = None
			self.pageSize = None
			self.startTime = None
			self.endTime = None
			self.returnIsvLotattrs = None

		def getapiname(self):
			return 'jingdong.eclp.checkstock.queryCheckStockProfit'

			





