from selenium.webdriver import Remote


class ReuseIe(Remote):
    def __init__(self, command_executor, session_id):
        self.r_session_id = session_id
        Remote.__init__(self, command_executor=command_executor, desired_capabilities={})

    def start_session(self, desired_capabilities, browser_profile=None):
        capabilities = {'desiredCapabilities': {}, 'requiredCapabilities': {}}
        for k, v in desired_capabilities.items():
            if k not in ('desiredCapabilities', 'requiredCapabilities'):
                capabilities['desiredCapabilities'][k] = v
            else:
                capabilities[k].update(v)
        if browser_profile:
            capabilities['desiredCapabilities']['firefox_profile'] = browser_profile.encoded

        self.session_id = self.r_session_id
        # self.capabilities = options.Options().to_capabilities()
        self.w3c = False