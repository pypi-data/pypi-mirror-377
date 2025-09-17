# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
import pytest

from ..reports import get_world_pedir


@pytest.mark.parametrize(
    ('orientation', 'pe_dir', 'expected'),
    [
        ('RAS', 'j', 'Posterior-Anterior'),
        ('RAS', 'j-', 'Anterior-Posterior'),
        ('RAS', 'i', 'Left-Right'),
        ('RAS', 'i-', 'Right-Left'),
        ('RAS', 'k', 'Inferior-Superior'),
        ('RAS', 'k-', 'Superior-Inferior'),
        ('LAS', 'j', 'Posterior-Anterior'),
        ('LAS', 'i-', 'Left-Right'),
        ('LAS', 'k-', 'Superior-Inferior'),
        ('LPI', 'j', 'Anterior-Posterior'),
        ('LPI', 'i-', 'Left-Right'),
        ('LPI', 'k-', 'Inferior-Superior'),
        ('SLP', 'k-', 'Posterior-Anterior'),
        ('SLP', 'k', 'Anterior-Posterior'),
        ('SLP', 'j-', 'Left-Right'),
        ('SLP', 'j', 'Right-Left'),
        ('SLP', 'i', 'Inferior-Superior'),
        ('SLP', 'i-', 'Superior-Inferior'),
    ],
)
def test_get_world_pedir(tmpdir, orientation, pe_dir, expected):
    assert get_world_pedir(orientation, pe_dir) == expected


def test_subject_summary_handles_missing_task(tmp_path):
    from ..reports import SubjectSummary

    t1w = tmp_path / 'sub-01_T1w.nii.gz'
    t1w.write_text('')
    pet1 = tmp_path / 'sub-01_task-rest_run-01_pet.nii.gz'
    pet1.write_text('')
    pet2 = tmp_path / 'sub-01_run-01_pet.nii.gz'
    pet2.write_text('')

    summary = SubjectSummary(
        t1w=[str(t1w)],
        pet=[str(pet1), str(pet2)],
        std_spaces=[],
        nstd_spaces=[],
    )

    segment = summary._generate_segment()
    assert 'Task: rest (1 run)' in segment
    assert 'Task: <none> (1 run)' in segment


def test_functional_summary_with_metadata():
    from ..reports import FunctionalSummary

    summary = FunctionalSummary(
        registration='mri_coreg',
        registration_dof=6,
        orientation='RAS',
        metadata={
            'TracerName': 'DASB',
            'TracerRadionuclide': '[11C]',
            'InjectedRadioactivity': 100,
            'InjectedRadioactivityUnits': 'MBq',
            'FrameTimesStart': [0, 1],
            'FrameDuration': [1, 1],
        },
    )

    segment = summary._generate_segment()
    assert 'Radiotracer: [11C]DASB' in segment
    assert 'Injected dose: 100 MBq' in segment
    assert 'Number of frames: 2' in segment
