from seven_jd.jd.api.base import RestApi

class DataVenderPreciseRecomActivityCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activity_info = None

		def getapiname(self):
			return 'jingdong.data.vender.precise.recom.activity.create'

			
	

class StrategyInfoVO(object):
		def __init__(self):
			"""
			"""
			self.strategyId = None
			self.strategyType = None
			self.strategyLevel = None


class InterestVO(object):
		def __init__(self):
			"""
			"""
			self.basic = None
			self.content = None
			self.interestType = None
			self.interestLevel = None
			self.enabled = None
			self.startTime = None
			self.endTime = None
			self.strategyList = None


class Activity_info(object):
		def __init__(self):
			"""
			"""
			self.activityName = None
			self.activityDesc = None
			self.startTime = None
			self.endTime = None
			self.resultType = None
			self.priority = None
			self.scene = None
			self.interests = None





