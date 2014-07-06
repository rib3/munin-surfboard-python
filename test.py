#!/usr/bin/env python

#from migrator.utils import verbosity_loglevel
import argparse
import unittest
import logging

parser = argparse.ArgumentParser(description='Run tests on drive-migrator')
# Accept testcase args when parsing, handled by uniitest.main()
parser.add_argument('args', metavar='TEST', nargs='*',
                    help='args?')
parser.add_argument('--verbose', '-v', action='count',
                    help='Increase verbosity (-v for INFO, -vv for DEBUG)')

def main():
    args = parser.parse_args()
    logging.basicConfig()
        #level=verbosity_loglevel(args.verbose, logging.CRITICAL))

    unittest.main(module='surfboard.tests')

if __name__ == '__main__':
    main()
