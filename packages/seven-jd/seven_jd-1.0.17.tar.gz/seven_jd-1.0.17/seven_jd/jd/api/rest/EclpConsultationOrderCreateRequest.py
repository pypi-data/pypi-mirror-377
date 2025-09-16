from seven_jd.jd.api.base import RestApi

class EclpConsultationOrderCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderType = None
			self.orderNo = None
			self.choosenPhoneNumber = None
			self.userPhoneNumber = None
			self.deptNo = None
			self.userInfoStr = None

		def getapiname(self):
			return 'jingdong.eclp.consultationOrder.create'

			





