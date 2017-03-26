import ConfigParser


class Options(ConfigParser.SafeConfigParser):

    def __init__(self, config_file, env):
        """

        :param config_file:
        :param env:
        """

        ConfigParser.SafeConfigParser.__init__(self)
        self.readfp(open(config_file))
        self.env = env
