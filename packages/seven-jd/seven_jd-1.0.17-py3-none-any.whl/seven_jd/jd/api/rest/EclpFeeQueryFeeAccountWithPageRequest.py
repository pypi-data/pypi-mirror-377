from seven_jd.jd.api.base import RestApi

class EclpFeeQueryFeeAccountWithPageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.accountNo = None
			self.accountDayStart = None
			self.accountDayEnd = None
			self.status = None
			self.currentPage = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.eclp.fee.queryFeeAccountWithPage'

			





