from seven_jd.jd.api.base import RestApi

class EclpRtwUpdateRtwOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eclpRtwNo = None
			self.isvRtwNum = None
			self.ownerNo = None
			self.packageNo = None
			self.shipperName = None
			self.senderName = None
			self.senderTelPhone = None
			self.senderMobilePhone = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.updateRtwOrder'

			





