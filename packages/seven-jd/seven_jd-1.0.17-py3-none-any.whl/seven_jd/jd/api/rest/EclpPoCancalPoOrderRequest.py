from seven_jd.jd.api.base import RestApi

class EclpPoCancalPoOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.poOrderNo = None

		def getapiname(self):
			return 'jingdong.eclp.po.cancalPoOrder'

			





