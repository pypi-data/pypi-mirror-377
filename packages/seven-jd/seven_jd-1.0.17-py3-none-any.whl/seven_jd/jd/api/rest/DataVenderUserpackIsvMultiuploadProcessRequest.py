from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvMultiuploadProcessRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.upload_id = None
			self.bytes = None
			self.length = None
			self.part_number = None
			self.md5 = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.multiupload.process'

			





