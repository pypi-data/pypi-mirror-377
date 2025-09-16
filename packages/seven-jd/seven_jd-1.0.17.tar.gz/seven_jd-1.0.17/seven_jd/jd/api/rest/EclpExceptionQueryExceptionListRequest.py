from seven_jd.jd.api.base import RestApi

class EclpExceptionQueryExceptionListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNos = None
			self.isvOrderNos = None
			self.orderType = None
			self.bizType = None
			self.createTimeStart = None
			self.createTimeEnd = None
			self.pageNo = None
			self.pageSize = None
			self.errCode = None

		def getapiname(self):
			return 'jingdong.eclp.exception.queryExceptionList'

			





