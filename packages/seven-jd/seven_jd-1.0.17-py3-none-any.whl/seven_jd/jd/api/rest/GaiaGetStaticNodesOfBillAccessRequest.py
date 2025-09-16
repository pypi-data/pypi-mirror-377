from seven_jd.jd.api.base import RestApi

class GaiaGetStaticNodesOfBillAccessRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.billType = None
			self.billCode = None
			self.businessType = None

		def getapiname(self):
			return 'jingdong.gaia.getStaticNodesOfBillAccess'

			





