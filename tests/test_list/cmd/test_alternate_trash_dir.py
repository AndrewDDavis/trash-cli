# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
from datetime import datetime

from tests.test_list.cmd.setup import Setup

from tests.support.asserts import assert_equals_with_unidiff
from tests.fake_trash_dir import FakeTrashDir


class TestAlternateTrashDir(Setup):

    def test_should_list_contents_of_alternate_trashdir(self):
        self.user.set_fake_uid(123)
        self.user.add_volume(self.top_dir)
        self.user.add_trashinfo(self.top_dir / '.Trash-123', 'file',
                                "2000-01-01")

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 %s/file\n" %
                                   self.top_dir, output.stdout)
