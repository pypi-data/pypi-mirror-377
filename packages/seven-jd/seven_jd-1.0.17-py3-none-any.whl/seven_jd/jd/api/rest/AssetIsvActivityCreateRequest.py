from seven_jd.jd.api.base import RestApi

class AssetIsvActivityCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activity_id = None
			self.activity_name = None
			self.begin_date = None
			self.end_date = None
			self.tool = None
			self.details = None

		def getapiname(self):
			return 'jingdong.asset.isv.activity.create'

			





