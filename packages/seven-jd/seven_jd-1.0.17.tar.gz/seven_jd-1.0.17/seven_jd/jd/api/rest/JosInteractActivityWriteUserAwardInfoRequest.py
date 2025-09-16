from seven_jd.jd.api.base import RestApi

class JosInteractActivityWriteUserAwardInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.appName = None
			self.channel = None
			self.interactPrizeId = None
			self.createTime = None
			self.prizeRuleId = None
			self.awardRecordId = None
			self.rfId = None
			self.batchId = None
			self.couponId = None
			self.prizeType = None
			self.discount = None
			self.activityId = None
			self.userPin = None
			self.quota = None
			self.activityEndTime = None
			self.batchKey = None
			self.activityType = None
			self.putKey = None
			self.activityStartTime = None
			self.vender = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.jos.interact.activity.writeUserAwardInfo'

			





