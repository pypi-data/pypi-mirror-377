from seven_jd.jd.api.base import RestApi

class JosInteractActivityWriteUserInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.appName = None
			self.channel = None
			self.sourceApp = None
			self.vender = None
			self.actionTime = None
			self.activityId = None
			self.userPin = None
			self.activityEndTime = None
			self.nickName = None
			self.activityStartTime = None
			self.actionType = None
			self.businessid = None
			self.activityType = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.jos.interact.activity.writeUserInfo'

			





