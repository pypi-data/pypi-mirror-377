from seven_jd.jd.api.base import RestApi

class InteractiveQueryInteractiveInfoJHubHttpRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sourceCode = None
			self.appKey = None
			self.assistEncryptAssignmentId = None
			self.assistInfoFlag = None
			self.inviteId = None
			self.assistNum = None
			self.needNum = None
			self.rewardEncryptAssignmentId = None
			self.timesEncryptAssignmentId = None
			self.lotteryEncryptAssignmentId = None
			self.lotteryStartTime = None
			self.lotteryEndTime = None
			self.lotteryNum = None
			self.rewardOrderType = None
			self.couponUsableGetSwitch = None
			self.userIncrRewardValid = None
			self.showRecievableStatus = None
			self.closeBI = None
			self.isQueryTrailInfo = None
			self.recentRewardInAssignmentId = None
			self.attribute2 = None
			self.account = None
			self.encryptProjectId = None
			self.attribute1 = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.interactive.queryInteractiveInfoJHubHttp'

			





