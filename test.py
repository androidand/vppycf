#!/usr/bin/env python3

import unittest
from helpers import getBuildAndRevision

print("Running tests")

class HelpersTest(unittest.TestCase):
	env = "Dev"
	build, revision = getBuildAndRevision(env)

	def test_build_is_correct(self):
		correct_build = "development"
		assert self.build == correct_build, 'Build is wrong'

	def test_revision_is_correct(self):
		correct_revision = "develop"
		assert self.revision == correct_revision, 'Revision is wrong'