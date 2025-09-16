from seven_jd.jd.api.base import RestApi

class LdopAlphaWaybillUnbindRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.platformOrderNo = None
			self.providerId = None
			self.providerCode = None
			self.operatorName = None
			self.operatorTime = None
			self.waybillCodeList = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.waybill.unbind'

			





