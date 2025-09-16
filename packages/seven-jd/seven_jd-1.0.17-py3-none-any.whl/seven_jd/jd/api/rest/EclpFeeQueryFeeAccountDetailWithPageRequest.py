from seven_jd.jd.api.base import RestApi

class EclpFeeQueryFeeAccountDetailWithPageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.accountNo = None
			self.billDayStart = None
			self.billDayEnd = None
			self.currentPage = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.eclp.fee.queryFeeAccountDetailWithPage'

			





