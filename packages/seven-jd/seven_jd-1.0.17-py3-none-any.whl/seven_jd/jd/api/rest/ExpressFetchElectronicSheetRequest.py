from seven_jd.jd.api.base import RestApi

class ExpressFetchElectronicSheetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.printObject = None
			self.userEnv = None
			self.printTemplate = None

		def getapiname(self):
			return 'jingdong.express.fetch.electronic.sheet'

			
	

class Value(object):
		def __init__(self):
			"""
			"""
			self.customProperty = None


class PrintObject(object):
		def __init__(self):
			"""
			"""
			self.waybillCodes = None
			self.electronicSheetType = None
			self.packageCodes = None
			self.boxCodes = None
			self.orderIds = None
			self.customProperties = None
			self.codeType = None


class UserEnv(object):
		def __init__(self):
			"""
			"""
			self.tradeCode = None


class PrintTemplate(object):
		def __init__(self):
			"""
			"""
			self.paperSize = None





