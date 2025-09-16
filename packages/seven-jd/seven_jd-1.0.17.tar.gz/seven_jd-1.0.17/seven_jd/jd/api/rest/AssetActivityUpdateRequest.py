from seven_jd.jd.api.base import RestApi

class AssetActivityUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.token = None
			self.begin_date = None
			self.end_date = None

		def getapiname(self):
			return 'jingdong.asset.activity.update'

			





