class ConfigModel:
    def __init__(self, configJSON):
        try:
            self.serverUrl = configJSON["server"]["serverUrl"]
            self.kafkaUrl = configJSON["server"]["kafkaUrl"]
            self.prjId = configJSON.get("key", {}).get("prjId", 0)
            self.xAccessKey = configJSON["key"]["xAccessKey"]
            self.xSecretKey = configJSON["key"]["xSecretKey"]
            self.pluginCode = configJSON["plugin"]["pluginCode"]
            self.pluginVersion = configJSON["plugin"]["pluginVersion"]
            self.taskFlowCode = configJSON["task"]["taskFlowCode"]
        except KeyError as e:
            raise KeyError(f"Missing required configuration key: {e}")

        if self.pluginVersion:
            self.uniquePluginCode = self.pluginCode + "-" + self.pluginVersion.replace(".", "-")
        else:
            self.uniquePluginCode = self.pluginCode

        self.headers = {
            'Content-Type': 'application/json',
            'X-Access-Key': self.xAccessKey,
            'X-Secret-Key': self.xSecretKey
        }
