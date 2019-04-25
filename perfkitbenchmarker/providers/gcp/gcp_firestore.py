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

from perfkitbenchmarker import flags
from perfkitbenchmarker import resource
from perfkitbenchmarker import vm_util

FLAGS = flags.FLAGS
flags.DEFINE_string('gcp_firestore_projectid',
                    'firestore-benchmark-tests',
                    'Google Project ID with firestore instance.')
flags.DEFINE_string('gcp_firestore_firebasecli_path', 'firebase',
                    'The path for the firebase utility.')


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
    """Collection is automatically created on load, TODO: Create json key."""
    pass

  def _Delete(self):
    """Deletes the collection, this currently needs npm and firebase cli."""
    cmd = [FLAGS.gcp_firestore_firebasecli_path,
           'firestore:delete', self.name,
           '--project', self.project,
           '-r',
           '-y']
    vm_util.IssueRetryableCommand(cmd)

  def _Exists(self):
    """Returns true if the collection exists, currently no way to check."""
    pass
