from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvMultiuploadStartRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.file_type = None
			self.file_size = None
			self.md5 = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.multiupload.start'

			





