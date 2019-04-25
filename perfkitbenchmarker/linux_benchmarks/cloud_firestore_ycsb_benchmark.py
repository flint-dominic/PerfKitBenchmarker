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

"""Run YCSB benchmark against Google Cloud Firestore

Before running this benchmark, you have to download your JSON
service account private key file to local machine, and pass the path
via 'cloud_firestore_ycsb_keyfile' parameters to PKB.

By default, this benchmark provision 1 single-CPU VM and spawn 1 thread
to test Firestore.
"""

from perfkitbenchmarker import configs
from perfkitbenchmarker import flags
from perfkitbenchmarker import vm_util
from perfkitbenchmarker.linux_packages import ycsb
from perfkitbenchmarker.providers.gcp import gcp_firestore


BENCHMARK_NAME = 'cloud_firestore_ycsb'
BENCHMARK_CONFIG = """
cloud_firestore_ycsb:
  description: >
      Run YCSB against Google Cloud Firestore. 
  vm_groups:
    default:
      vm_spec: *default_single_core
      vm_count: 1"""

PRIVATE_KEYFILE_DIR = '/tmp/serviceAccountKey.json'

FLAGS = flags.FLAGS
flags.DEFINE_string('cloud_firestore_ycsb_keyfile',
                    'serviceAccountKey.json',
                    'The path to Google API JSON private key file.')
flags.DEFINE_string('cloud_firestore_ycsb_debug',
                    'false',
                    'The logging level when running YCSB.')


def GetConfig(user_config):
  config = configs.LoadConfig(BENCHMARK_CONFIG, user_config, BENCHMARK_NAME)
  if FLAGS['ycsb_client_vms'].present:
    config['vm_groups']['default']['vm_count'] = FLAGS.ycsb_client_vms
  return config


def CheckPrerequisites(benchmark_config):
  """Verifies that the required resources are present.
  Raises:
  perfkitbenchmarker.data.ResourceNotFound: On missing resource.
  """
  if not FLAGS.cloud_firestore_ycsb_keyfile:
    raise ValueError('"cloud_firestore_ycsb_keyfile" must be set')


def Prepare(benchmark_spec):
  """Install YCSB on the target vm.
  Args:
  benchmark_spec: The benchmark specification. Contains all data that is
      required to run the benchmark.
  """
  benchmark_spec.always_call_cleanup = True

  benchmark_spec.firestore_instance = gcp_firestore.GcpFirestoreInstance(
      'pkb-{0}'.format(FLAGS.run_uri), FLAGS.zones[0])

  vms = benchmark_spec.vms
  vm_util.RunThreaded(_Install, vms)

  benchmark_spec.executor = ycsb.YCSBExecutor('googlefirestore')


def Run(benchmark_spec):
  """Run YCSB on the target vm.
  Args:
  benchmark_spec: The benchmark specification. Contains all data that is
  required to run the benchmark.
  Returns:
  A list of sample.Sample objects.
  """
  vms = benchmark_spec.vms
  run_kwargs = {
      'googlefirestore.serviceAccountKey': PRIVATE_KEYFILE_DIR,
      'googlefirestore.projectId': FLAGS.gcp_firestore_projectid,
      'googlefirestore.debug': FLAGS.cloud_firestore_ycsb_debug,
      'table': 'pkb-{0}'.format(FLAGS.run_uri),
  }
  load_kwargs = run_kwargs.copy()
  if FLAGS['ycsb_preload_threads'].present:
    load_kwargs['threads'] = FLAGS['ycsb_preload_threads']
  samples = list(benchmark_spec.executor.LoadAndRun(
      vms, load_kwargs=load_kwargs, run_kwargs=run_kwargs))
  return samples


def Cleanup(benchmark_spec):
  """Cleanup YCSB on the target vm.
  Args:
  benchmark_spec: The benchmark specification. Contains all data that is
  required to run the benchmark.
  """
  benchmark_spec.firestore_instance.Delete()


def _Install(vm):
  """Install YCSB on client 'vm', and copy private key."""
  vm.Install('ycsb')
  vm.RemoteCopy(FLAGS.cloud_firestore_ycsb_keyfile, PRIVATE_KEYFILE_DIR)
