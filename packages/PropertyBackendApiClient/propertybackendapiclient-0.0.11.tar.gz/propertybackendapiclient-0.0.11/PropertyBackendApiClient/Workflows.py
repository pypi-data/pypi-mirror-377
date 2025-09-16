# Workflows class to be moved into client

class Stage():
    stage_id = None
    wfdict = None
    def __init__(self, stage_id, wfdict):
        self.stage_id = stage_id
        self.wfdict = wfdict

    def getId(self):
        return self.wfdict["id"]

    def getName(self):
        return self.wfdict["name"]

    def isActive(self):
        if "active" not in self.wfdict:
            return False
        return self.wfdict["active"]

    def getFailedStageId(self):
        if "progression" not in self.wfdict:
            return None
        if "failed" not in self.wfdict["progression"]:
            return None
        return self.wfdict["progression"]["failed"]

class Workflow():
    wfdict = None
    def __init__(self, wfdict):
        if "id" not in wfdict:
            raise Exception("Workflow without ID")
        self.wfdict = wfdict
        stage_objects = {}
        for stage_id in self.wfdict["stages"]:
            stage_objects[stage_id] = Stage(stage_id, self.wfdict["stages"][stage_id])
        self.wfdict["stages"] = stage_objects

    def getId(self):
        return self.wfdict["id"]

    def getName(self):
        return self.wfdict["name"]

    def getInitialStage(self):
        return self.wfdict["initial_stage"]

    def getStages(self):
        return self.wfdict["stages"]

    def getStage(self, stage_id):
        return self.wfdict["stages"][stage_id]

class Workflows():
    wfdict = None
    def __init__(self, wfdict):
        if "id" not in wfdict:
            raise Exception("Trying to load workflows object with wrong data - no id")
        if wfdict["id"] != "workflows":
            raise Exception("Trying to load workflows object with wrong data - wrong id got " + wfdict["id"])
        if "workflows" not in wfdict:
            raise Exception("Trying to load workflows object with wrong data - no workflows")
        self.wfdict = {}
        for wf_id in wfdict["workflows"]:
            wfo = Workflow(wfdict["workflows"][wf_id])
            self.wfdict[wfo.getId()] = wfo

    def getWorkflow(self, wf_id):
        return self.wfdict[wf_id]
