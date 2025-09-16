from seven_jd.jd.api.base import RestApi

class SecurityOrderinfoLogUploadRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderInfoLog = None

		def getapiname(self):
			return 'jingdong.security.orderinfo.log.upload'

			
	

class OrderOaidInfo(object):
		def __init__(self):
			"""
			"""
			self.receiver_name = None
			self.receiver_phone = None
			self.order_id = None
			self.receiver_addr = None
			self.oaid = None


class OrderInfoLog(object):
		def __init__(self):
			"""
			"""
			self.user_ip = None
			self.josAppKey = None
			self.jd_id = None
			self.device_id = None
			self.url = None
			self.app_name = None
			self.user_id = None
			self.file_md5 = None
			self.orderOaidInfoList = None
			self.operation = None
			self.timestamp = None





