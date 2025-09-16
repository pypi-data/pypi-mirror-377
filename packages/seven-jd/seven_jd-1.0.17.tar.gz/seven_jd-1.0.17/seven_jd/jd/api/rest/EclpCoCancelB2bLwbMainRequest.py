from seven_jd.jd.api.base import RestApi

class EclpCoCancelB2bLwbMainRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNo = None
			self.wbNo = None

		def getapiname(self):
			return 'jingdong.eclp.co.cancelB2bLwbMain'

			





