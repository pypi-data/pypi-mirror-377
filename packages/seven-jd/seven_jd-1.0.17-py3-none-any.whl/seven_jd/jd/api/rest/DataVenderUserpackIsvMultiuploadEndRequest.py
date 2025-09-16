from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvMultiuploadEndRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.upload_id = None
			self.result_name = None
			self.result_desc = None
			self.last_part_number = None
			self.data_type = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.multiupload.end'

			





