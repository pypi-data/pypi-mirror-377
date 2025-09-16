from seven_jd.jd.api.base import RestApi

class PopPopCommentJsfServiceSaveReplyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.commentId = None
			self.content = None
			self.replyId = None

		def getapiname(self):
			return 'jingdong.pop.PopCommentJsfService.saveReply'

			





