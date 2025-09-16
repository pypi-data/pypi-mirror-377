from seven_jd.jd.api.base import RestApi

class InteractCenterCreateGiftActivityRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.param1 = None
			self.param2 = None

		def getapiname(self):
			return 'jingdong.interactCenter.createGiftActivity'

			
	

class Param1(object):
		def __init__(self):
			"""
			"""
			self.appName = None
			self.appId = None
			self.clientIp = None
			self.channel = None


class Attribute1(object):
		def __init__(self):
			"""
			"""
			self.discount = None
			self.quota = None
			self.validateDay = None
			self.prizeType = None
			self.sendCount = None
			self.assetItemId = None
			self.awardType = None
			self.floatRatio = None
			self.batchKey = None


class Param2(object):
		def __init__(self):
			"""
			"""
			self.giftRuleActivityList = None
			self.type = None
			self.startTime = None
			self.name = None
			self.endTime = None
			self.venderMemberLevel = None
			self.creator = None
			self.supplierCode = None





