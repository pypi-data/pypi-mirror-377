from seven_jd.jd.api.base import RestApi

class AssetIsvAccountBalanceQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.type_id = None

		def getapiname(self):
			return 'jingdong.asset.isv.account.balance.query'

			





