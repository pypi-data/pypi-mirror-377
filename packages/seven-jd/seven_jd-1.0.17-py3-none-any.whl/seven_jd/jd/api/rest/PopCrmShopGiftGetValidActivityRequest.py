from seven_jd.jd.api.base import RestApi

class PopCrmShopGiftGetValidActivityRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.channel = None

		def getapiname(self):
			return 'jingdong.pop.crm.shopGift.getValidActivity'

			





