from seven_jd.jd.api.base import RestApi

class InteractiveQueryInteractiveRewardInfoJHubSdkRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sourceCode = None
			self.appKey = None
			self.detailTypeFlag = None
			self.currentPage = None
			self.pageSize = None
			self.needExchangeRestScore = None
			self.needProjectTotalRewards = None
			self.needPoolRewards = None
			self.needAssignmentRewards = None
			self.needRewardType = None
			self.needWinningStatus = None
			self.encryptProjectPoolId = None
			self.account = None
			self.encryptProjectId = None
			self.attribute1 = None
			self.projectFailRewardsFlag = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.interactive.queryInteractiveRewardInfoJHubSdk'

			





