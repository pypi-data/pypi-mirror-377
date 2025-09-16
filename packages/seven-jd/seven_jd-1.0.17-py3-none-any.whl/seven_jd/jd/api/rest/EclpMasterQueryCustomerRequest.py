from seven_jd.jd.api.base import RestApi

class EclpMasterQueryCustomerRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.sellerNo = None
			self.customerNo = None
			self.customerName = None
			self.warehouseNo = None
			self.sellerName = None
			self.pageNo = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.eclp.master.queryCustomer'

			





