from seven_jd.jd.api.base import RestApi

class EclpOrderQueryOrderListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.startDate = None
			self.endDate = None
			self.shopNo = None
			self.warehouseNo = None
			self.pageNo = None
			self.pageSize = None
			self.salePlatformOrderNo = None
			self.orderStatus = None

		def getapiname(self):
			return 'jingdong.eclp.order.queryOrderList'

			





