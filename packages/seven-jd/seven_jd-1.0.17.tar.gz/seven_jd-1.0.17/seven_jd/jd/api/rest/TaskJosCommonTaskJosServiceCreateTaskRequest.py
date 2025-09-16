from seven_jd.jd.api.base import RestApi

class TaskJosCommonTaskJosServiceCreateTaskRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.actionTime = None
			self.dataGroupIdLv1 = None
			self.type = None
			self.dataGroupIdLv2 = None
			self.dataGroupIdLv3 = None
			self.dataGroupIdLv4 = None
			self.dataInstId = None
			self.name = None
			self.sendNumber = None
			self.content = None
			self.templateId = None

		def getapiname(self):
			return 'jingdong.task.jos.CommonTaskJosService.createTask'

			





