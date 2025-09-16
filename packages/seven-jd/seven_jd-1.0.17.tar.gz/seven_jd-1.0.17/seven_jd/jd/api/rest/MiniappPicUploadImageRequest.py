from seven_jd.jd.api.base import RestApi

class MiniappPicUploadImageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.picBase64 = None

		def getapiname(self):
			return 'jingdong.miniapp.pic.uploadImage'

			





