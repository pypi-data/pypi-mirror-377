from seven_jd.jd.api.base import RestApi

class SubmitIndustryInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.industryInfoDto = None

		def getapiname(self):
			return 'jingdong.submitIndustryInfo'

			
	

class IndustryInfoDto(object):
		def __init__(self):
			"""
			"""
			self.realName = None
			self.education = None
			self.data = None
			self.mobileNumber = None
			self.schoolSystem = None
			self.graduateTime = None
			self.startYear = None
			self.idNumber = None
			self.schoolName = None
			self.channelSource = None





