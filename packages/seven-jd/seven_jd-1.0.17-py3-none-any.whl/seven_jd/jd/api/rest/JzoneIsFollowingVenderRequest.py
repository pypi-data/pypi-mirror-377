from seven_jd.jd.api.base import RestApi

class JzoneIsFollowingVenderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activityId = None
			self.encryptOpenId = None

		def getapiname(self):
			return 'jingdong.jzone.isFollowingVender'

			





