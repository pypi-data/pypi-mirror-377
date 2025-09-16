from seven_jd.jd.api.base import RestApi

class DongdongPacketJosChatMessagePushRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.param1 = None
			self.param2 = None

		def getapiname(self):
			return 'jingdong.dongdong.packet.josChatMessage.push'

			
	

class Param1(object):
		def __init__(self):
			"""
			"""
			self.accessid = None
			self.aspid = None
			self.source = None
			self.accessToken = None
			self.version = None


class Param2(object):
		def __init__(self):
			"""
			"""
			self.upid = None
			self.ver = None
			self.fromApp = None
			self.fromClientType = None
			self.fromPin = None
			self.toApp = None
			self.toClientType = None
			self.toPin = None
			self.body = None
			self.open_id_buyer = None
			self.xid_buyer = None





