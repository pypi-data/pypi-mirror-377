from seven_jd.jd.api.base import RestApi

class LdopMiddleWaybillWaybillPickupApiRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.vendorCode = None
			self.pickupCode = None

		def getapiname(self):
			return 'jingdong.ldop.middle.waybill.WaybillPickupApi'

			





