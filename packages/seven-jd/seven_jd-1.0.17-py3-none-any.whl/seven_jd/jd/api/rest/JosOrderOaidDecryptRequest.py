from seven_jd.jd.api.base import RestApi

class JosOrderOaidDecryptRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.getReceiverInfoListReqVO = None

		def getapiname(self):
			return 'jingdong.jos.order.oaid.decrypt'

			
	

class Attribute1(object):
		def __init__(self):
			"""
			"""
			self.orderId = None
			self.oaid = None


class GetReceiverInfoListReqVO(object):
		def __init__(self):
			"""
			"""
			self.orderType = None
			self.appName = None
			self.extendProps = None
			self.orderInfos = None
			self.expiration = None
			self.region = None
			self.scenesType = None





