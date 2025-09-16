from seven_jd.jd.api.base import RestApi

class OrderOrderDeleteApplyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.order_id = None
			self.del_apply_type = None
			self.del_apply_reason = None

		def getapiname(self):
			return 'jingdong.order.orderDelete.apply'

			





