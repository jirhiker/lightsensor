# ===============================================================================
# Copyright 2016 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import glob
import os


def unique_path(root, base, delimiter='-', extension='.txt', width=3):
    """
        unique_path suffers from the fact that it starts at 001.
        this is a problem for log files because the logs are periodically archived which means
        low paths are removed.

        unique_path2 solves this by finding the max path then incrementing by 1
    """
    if not extension.startswith('.'):
        extension = '.{}'.format(extension)

    cnt = max_path_cnt(root, '{}-'.format(base), delimiter=delimiter, extension=extension)
    p = os.path.join(root, '{{}}-{{:0{}d}}{{}}'.format(width).format(base, cnt, extension))
    return p


def max_path_cnt(root, base, delimiter='-', extension='.txt'):
    """

    :param root:
    :param base:
    :param extension:
    :return: int max+1
    """
    basename = '{}*{}'.format(base, extension)
    cnt = 0

    for p in glob.iglob(os.path.join(root, basename)):
        p = os.path.basename(p)
        head, tail = os.path.splitext(p)

        cnt = max(int(head.split(delimiter)[-1]), cnt)

    cnt += 1
    return cnt

# ============= EOF =============================================
