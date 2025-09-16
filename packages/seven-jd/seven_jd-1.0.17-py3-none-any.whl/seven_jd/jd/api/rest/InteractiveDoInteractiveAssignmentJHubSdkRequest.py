from seven_jd.jd.api.base import RestApi

class InteractiveDoInteractiveAssignmentJHubSdkRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sourceCode = None
			self.appKey = None
			self.exchangeNum = None
			self.rewardCustomQuantity = None
			self.riskLabel = None
			self.hbTraceId = None
			self.fansLevel = None
			self.umcTraceId = None
			self.umcExtMapStr = None
			self.interactNum = None
			self.customRewardCondition = None
			self.customExtInfo = None
			self.itemId = None
			self.actionType = None
			self.itemContent = None
			self.account = None
			self.amount = None
			self.encryptProjectId = None
			self.encryptAssignmentId = None
			self.completionFlag = None
			self.assignmentId = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.interactive.doInteractiveAssignmentJHubSdk'

			





