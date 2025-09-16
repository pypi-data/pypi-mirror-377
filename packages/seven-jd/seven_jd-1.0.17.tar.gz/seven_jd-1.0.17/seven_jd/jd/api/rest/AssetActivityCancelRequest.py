from seven_jd.jd.api.base import RestApi

class AssetActivityCancelRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.token = None
			self.remark = None

		def getapiname(self):
			return 'jingdong.asset.activity.cancel'

			





