from seven_jd.jd.api.base import RestApi

class OrderOperateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.data = None

		def getapiname(self):
			return 'jingdong.order.operate'

			





