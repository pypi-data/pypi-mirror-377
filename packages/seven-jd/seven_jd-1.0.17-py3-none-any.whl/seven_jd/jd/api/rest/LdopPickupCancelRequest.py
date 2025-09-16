from seven_jd.jd.api.base import RestApi

class LdopPickupCancelRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.endReasonName = None
			self.endReason = None
			self.pickupCode = None
			self.source = None
			self.customerCode = None

		def getapiname(self):
			return 'jingdong.ldop.pickup.cancel'

			





