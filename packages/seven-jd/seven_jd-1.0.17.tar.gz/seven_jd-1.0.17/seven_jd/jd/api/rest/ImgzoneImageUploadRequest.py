from seven_jd.jd.api.base import RestApi

class ImgzoneImageUploadRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.belongType = None
			self.accessToken = None
			self.callEnd = None
			self.imgName = None
			self.cateId = None
			self.imgFile = None

		def getapiname(self):
			return 'jingdong.imgzone.image.upload'

			





