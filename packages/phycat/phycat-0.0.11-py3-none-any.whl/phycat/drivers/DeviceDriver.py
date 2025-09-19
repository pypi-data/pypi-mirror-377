from phycat import PhycatSession


class PhycatDeviceDriver:
    def __init__(self, session : PhycatSession, handle: int, parameters: dict = {}):
        self.session : PhycatSession = session
