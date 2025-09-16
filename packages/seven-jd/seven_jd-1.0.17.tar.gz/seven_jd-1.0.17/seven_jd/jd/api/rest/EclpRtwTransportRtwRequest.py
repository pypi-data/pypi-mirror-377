from seven_jd.jd.api.base import RestApi

class EclpRtwTransportRtwRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eclpSoNo = None
			self.eclpRtwNo = None
			self.isvRtwNum = None
			self.warehouseNo = None
			self.reson = None
			self.orderInType = None
			self.customField = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.transportRtw'

			





