from seven_jd.jd.api.base import RestApi

class EclpStockQueryGoodsLevelChangeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNo = None
			self.outLevel = None
			self.intoLevel = None
			self.pageNo = None
			self.pageSize = None
			self.startTime = None
			self.endTime = None

		def getapiname(self):
			return 'jingdong.eclp.stock.queryGoodsLevelChange'

			





