from seven_jd.jd.api.base import RestApi

class EclpSpareQueryTransOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptName = None
			self.orderType = None
			self.destWarehouseNo = None
			self.sellerName = None
			self.sellerNo = None
			self.pageSize = None
			self.startTime = None
			self.startWarehouseNo = None
			self.endTime = None
			self.type = None
			self.pageNum = None
			self.deptNo = None

		def getapiname(self):
			return 'jingdong.eclp.spare.queryTransOrder'

			





