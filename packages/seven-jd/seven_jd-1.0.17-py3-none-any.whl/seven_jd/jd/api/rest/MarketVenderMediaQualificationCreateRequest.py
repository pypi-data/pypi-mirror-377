from seven_jd.jd.api.base import RestApi

class MarketVenderMediaQualificationCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.merchantQualificationVo = None

		def getapiname(self):
			return 'jingdong.market.vender.media.qualification.create'

			
	

class Attribute1(object):
		def __init__(self):
			"""
			"""
			self.mulitiFileName = None
			self.busiType = None
			self.md5 = None
			self.fileUrl = None


class MerchantQualificationVo(object):
		def __init__(self):
			"""
			"""
			self.qualificationDesc = None
			self.mulitiFileDatas = None
			self.venderId = None
			self.appKey = None
			self.qualificationName = None





