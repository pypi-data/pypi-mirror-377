from seven_jd.jd.api.base import RestApi

class EclpOvasTransportGoodOvasItemsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.request = None

		def getapiname(self):
			return 'jingdong.eclp.ovas.transportGoodOvasItems'

			
	

class VasRequest(object):
		def __init__(self):
			"""
			"""
			self.serviceCode = None
			self.goodsDemand = None
			self.status = None


class GoodsNoVasRequest(object):
		def __init__(self):
			"""
			"""
			self.goodsNo = None
			self.vasRequestList = None


class Request(object):
		def __init__(self):
			"""
			"""
			self.deptName = None
			self.goodsNoVasRequestList = None
			self.sellerName = None
			self.deptId = None
			self.sellerNo = None
			self.deptNo = None





