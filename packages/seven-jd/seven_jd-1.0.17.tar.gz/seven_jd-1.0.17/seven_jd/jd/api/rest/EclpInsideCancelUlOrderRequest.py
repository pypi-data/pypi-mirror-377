from seven_jd.jd.api.base import RestApi

class EclpInsideCancelUlOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.ulNo = None
			self.outUlNo = None
			self.deptNo = None
			self.wareHouseNo = None

		def getapiname(self):
			return 'jingdong.eclp.inside.cancelUlOrder'

			





