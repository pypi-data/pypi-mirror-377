from seven_jd.jd.api.base import RestApi

class AssetBenefitQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.page_num = None
			self.page_size = None
			self.token = None

		def getapiname(self):
			return 'jingdong.asset.benefit.query'

			





