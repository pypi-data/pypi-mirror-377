from seven_jd.jd.api.base import RestApi

class RdmanBizcenterMaliciousOrderAddMaliciousRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.memo = None
			self.status = None
			self.reason = None
			self.theOrders = None
			self.relationPhone = None
			self.relationName = None
			self.fileName = None
			self.fileByte = None

		def getapiname(self):
			return 'jingdong.rdman.bizcenter.maliciousOrder.addMalicious'

			





