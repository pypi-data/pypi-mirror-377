from seven_jd.jd.api.base import RestApi

class ExpressOrderUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderInfoUpdateBeforePickupDTO = None

		def getapiname(self):
			return 'jingdong.express.order.update'

			
	

class OrderInfoUpdateBeforePickupDTO(object):
		def __init__(self):
			"""
			"""
			self.deliveryId = None
			self.customerCode = None
			self.weight = None
			self.packageCount = None
			self.volume = None
			self.orderId = None





