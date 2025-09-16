from seven_jd.jd.api.base import RestApi

class LdopMiddleWaybillWaybill2CTraceApiRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.tradeCode = None
			self.waybillCode = None

		def getapiname(self):
			return 'jingdong.ldop.middle.waybill.Waybill2CTraceApi'

			





