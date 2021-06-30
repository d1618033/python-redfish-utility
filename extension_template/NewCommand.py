# -*- coding: utf-8 -*-
""" New Command for RDMC """

import sys

from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS

class NewCommand():
    """ Main new command template class """
    def __init__(self):
        self.ident = {
            'name':'newcommand',
            'usage' : None,
            'description': "Run to show the new command is "
                     "working\n\texample: newcommand",
            'summary':'New command tutorial.',
            'aliases': [],
            'auxcommands': []
        }

        #self.definearguments(self.parser)
        self.cmdbase = None
        self.rdmc = None
        self.auxcommands = dict()

    def newcommandfunction(self, options=None):
        """ Main new command worker function

        :param options: command options
        :type options: options.
        """

        # TODO: This is where you would add your main worker code
        #       Refer to other commands for an example of this function
        sys.stdout.write(u"Hello World. It's me %s.\n" % options.name)

    def run(self, line, help_disp=False):
        """ Wrapper function for new command main function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self.rdmc.rdmc_parse_arglist(self, line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        #validation checks
        self.newcommandvalidation()
        self.newcommandfunction(options)

        #logout routine
        self.cmdbase.logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def newcommandvalidation(self):
        """ new command method validation function """
        try:
			# TODO: Any validation required need to be placed here.
			#       Refer to other commands for an example of this function
            pass
        except:
            raise

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        # TODO: This is where you add all your command line arguments.
        #       For more information on this section research optparse for python

        customparser.add_argument(
            '--name',
            dest='name',
            help="""Use the provided the output name.""",
            default="REDFISH",
        )

