from seven_jd.jd.api.base import RestApi

class InteractiveRewardSdkUnionQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.appKey = None
			self.sourceCode = None
			self.account = None
			self.pageNo = None
			self.encryptProjectIds = None
			self.pageSize = None
			self.encryptAssignmentIds = None
			self.rewardTypes = None
			self.assignmentTypes = None
			self.extRewardTypesStr = None
			self.extAssignmentTypesStr = None
			self.needCouponStatus = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.interactive.reward.sdkUnion.query'

			





