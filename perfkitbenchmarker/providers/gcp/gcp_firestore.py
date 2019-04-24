# Copyright 2019 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module containing class for GCP's firestore instances.

Collections can be created and deleted.
"""

import logging

from perfkitbenchmarker import flags
from perfkitbenchmarker import resource
from perfkitbenchmarker.providers.gcp import util

FLAGS = flags.FLAGS
flags.DEFINE_string('gcp_firestore_projectid',
                    'firestore-benchmark-tests',
                    'Google Project ID with firestore instance.')


class GcpFirestoreInstance(resource.BaseResource):
  """Object representing a GCP Firestore Instance.

  Attributes:
    name: Collection name.
    project: Enclosing project for the instance.
    zone: zone of the instance's cluster.
  """

  def __init__(self, name, zone):
    super(GcpFirestoreInstance, self).__init__()
    self.name = name
    self.zone = zone
    self.project = FLAGS.gcp_firestore_projectid

  def _Create(self):
    """Creates the key, collection is automatically created on load."""
    cmd = util.GcloudCommand(self,
                             'iam',
                             'service-accounts',
                             'create', self.name)
    cmd.flags['display-name'] = self.name
    stdout, stderr, retcode = cmd.Issue()
    logging.error('Unable to create service account. Return code {0} '
                  'STDOUT: {1}\nSTDERR: {2}'.format(retcode, stdout, stderr))

    cmd = util.GcloudCommand(self,
                             'iam',
                             'service-accounts',
                             'keys',
                             'create', FLAGS.cloud_firestore_ycsb_keyfile,
                             '--iam-account', '{0}@{1}.iam.gserviceaccount.com'
                             .format(self.name, FLAGS.gcp_firestore_projectid))
    stdout, stderr, retcode = cmd.Issue()
    logging.error('Unable to link role. Return code {0} '
                  'STDOUT: {1}\nSTDERR: {2}'.format(retcode, stdout, stderr))

  def _Delete(self):
    """Deletes the collection."""
    cmd = util.FirebaseCommand(self, 'firestore:delete', self.name, '--project', self.project, '-r', '-y')
    cmd.Issue()

    # # TODO: get key-id from create
    # cmd = util.GcloudCommand(self,
    #                          'iam',
    #                          'service-accounts',
    #                          'keys',
    #                          'delete', FLAGS.cloud_firestore_ycsb_keyfile,
    #                          '--iam-account', '{0}@{1}.iam.gserviceaccount.com'
    #                          .format(self.name, FLAGS.gcp_firestore_projectid))
    # stdout, stderr, retcode = cmd.Issue()
    # logging.error('Unable to delete keys. Return code {0} '
    #               'STDOUT: {1}\nSTDERR: {2}'.format(retcode, stdout, stderr))
    #
    # # TODO: fix quiet flag, get error if not deleted?
    # cmd = util.GcloudCommand(self,
    #                          'iam',
    #                          'service-accounts',
    #                          'delete',
    #                          '{0}@{1}.iam.gserviceaccount.com'
    #                          .format(self.name, FLAGS.gcp_firestore_projectid))
    # cmd.flags['quiet']
    # stdout, stderr, retcode = cmd.Issue()
    # logging.error('Unable to delete service account. Return code {0} '
    #               'STDOUT: {1}\nSTDERR: {2}'.format(retcode, stdout, stderr))

  def _Exists(self):
    """Returns true if the collection exists."""
