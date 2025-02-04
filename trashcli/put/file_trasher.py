# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy

from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.context import Context
from trashcli.put.core.trash_result import TrashResult
from trashcli.put.core.trashee import Trashee
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.volume_of_parent import VolumeOfParent
from trashcli.put.janitor import Janitor
from trashcli.put.my_logger import MyLogger
from trashcli.put.reporting.trash_put_reporter import TrashPutReporter
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder


class FileTrasher:

    def __init__(self,
                 volumes,  # type: VolumeOf
                 trash_directories_finder,  # type: TrashDirectoriesFinder
                 parent_realpath_fs,  # type: ParentRealpathFs
                 logger,  # type: MyLogger
                 reporter,  # type: TrashPutReporter
                 janitor,  # type: Janitor
                 volume_of_parent,  # type: VolumeOfParent
                 ):  # type: (...) -> None
        self.volumes = volumes
        self.trash_directories_finder = trash_directories_finder
        self.parent_realpath_fs = parent_realpath_fs
        self.logger = logger
        self.reporter = reporter
        self.janitor = janitor
        self.volume_of_parent = volume_of_parent or volume_of_parent

    def trash_file(self,
                   path,  # type: str
                   context,  # type: Context
                   ):
        volume = self._figure_out_volume(path, context.forced_volume)
        trashee = Trashee(path, volume)
        candidates = self._select_candidates(volume, context.user_trash_dir,
                                             context.environ,
                                             context.uid, context.home_fallback)
        failures = []
        for candidate in candidates:
            self.logger.log_put(self.reporter.trash_dir_with_volume(candidate),
                                context.log_data)
            trashing = self.janitor.trash_file_in(
                candidate, context.log_data, context.environ, trashee)
            if trashing.succeeded():
                self.logger.log_put(
                    self.reporter.file_has_been_trashed_in_as(path,
                                                              candidate,
                                                              context.environ),
                    context.log_data)
                return TrashResult.Success
            else:
                failures.append((candidate, trashing.reason))
        self.logger.log_put(self.reporter.unable_to_trash_file(
            trashee, failures, context.environ), context.log_data)
        return TrashResult.Failure

    def _figure_out_volume(self, path, default_volume):
        if default_volume:
            return default_volume
        else:
            return self.volume_of_parent.volume_of_parent(path)

    def _select_candidates(self, volume, user_trash_dir, environ, uid,
                           home_fallback):
        return self.trash_directories_finder. \
            possible_trash_directories_for(volume,
                                           user_trash_dir, environ, uid,
                                           home_fallback)
