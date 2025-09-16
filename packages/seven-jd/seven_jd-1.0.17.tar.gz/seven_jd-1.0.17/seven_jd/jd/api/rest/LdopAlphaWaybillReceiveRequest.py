from seven_jd.jd.api.base import RestApi

class LdopAlphaWaybillReceiveRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.content = None

		def getapiname(self):
			return 'jingdong.ldop.alpha.waybill.receive'

			





