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

import json
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

  def __init__(self, name, project, zone):
    super(GcpFirestoreInstance, self).__init__()
    self.name = name
    self.zone = zone
    self.project = project

  def _Create(self):
    """Creates the key, collection is automatically created on load."""
    cmd = util.GcloudCommand(self, 'iam', 'service-accounts', 'create',
                             self.name)
    cmd.flags['display-name'] = self.name
    stdout, stderr, retcode = cmd.Issue()

  def _Delete(self):
    """Deletes the collection."""
    cmd = util.FirebaseCommand(self, 'firestore:delete', self.name, 'r', 'y')
    cmd.Issue()

  def _Exists(self):
    """Returns true if the collection exists."""
    cmd = util.GcloudCommand(self, 'beta', 'bigtable', 'instances', 'list')
    cmd.flags['format'] = 'json'
    cmd.flags['project'] = self.project
    # The zone flag makes this command fail.
    cmd.flags['zone'] = []
    stdout, stderr, retcode = cmd.Issue(suppress_warning=True)
    if retcode != 0:
      # This is not ideal, as we're returning false not because we know
      # the table isn't there, but because we can't figure out whether
      # it is there.  This behavior is consistent without other
      # _Exists methods.
      logging.error('Unable to list GCP Bigtable instances. Return code %s '
                    'STDOUT: %s\nSTDERR: %s', retcode, stdout, stderr)
      return False
    result = json.loads(stdout)
    instances = {instance['name'] for instance in result}
    full_name = 'projects/{}/instances/{}'.format(self.project, self.name)
    return full_name in instances
