from seven_jd.jd.api.base import RestApi

class AssetBenefitSendRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.type_id = None
			self.item_id = None
			self.quantity = None
			self.user_pin = None
			self.token = None
			self.request_id = None
			self.remark = None
			self.ip = None
			self.phoneNum = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.asset.benefit.send'

			





