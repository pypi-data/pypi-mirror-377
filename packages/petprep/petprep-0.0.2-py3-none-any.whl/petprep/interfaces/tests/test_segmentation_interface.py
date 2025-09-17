from pathlib import Path
from types import SimpleNamespace

from ... import config
from ..segmentation import MRISclimbicSeg, SegmentBS, SegmentGTM, SegmentWM, _set_freesurfer_seed


def test_segmentgtm_skip(tmp_path):
    subj_dir = tmp_path / 'sub-01'
    (subj_dir / 'mri').mkdir(parents=True)
    (subj_dir / 'stats').mkdir()
    (subj_dir / 'mri' / 'gtmseg.mgz').write_text('')
    (subj_dir / 'stats' / 'gtmseg.stats').write_text('')

    seg = SegmentGTM(subjects_dir=str(tmp_path), subject_id='sub-01')
    res = seg.run()

    assert res.runtime.returncode == 0
    assert Path(res.outputs.out_file) == subj_dir / 'mri' / 'gtmseg.mgz'
    assert res.runtime.environ['FREESURFER_RANDOM_SEED'] == str(config.seeds.freesurfer)


def test_mrisclimbicseg_seed(tmp_path):
    subjects_dir = tmp_path / 'subjects'
    subject_dir = subjects_dir / 'sub-01'
    subject_dir.mkdir(parents=True)

    out_file = subject_dir / 'sub-01_sclimbic.nii.gz'
    out_stats = subject_dir / 'sub-01_sclimbic.stats'
    out_file.write_text('')
    out_stats.write_text('')

    seg = MRISclimbicSeg(out_file=str(out_file), sd=str(subjects_dir), subjects=['sub-01'])
    res = seg.run()

    assert res.runtime.returncode == 0
    assert res.runtime.environ['FREESURFER_RANDOM_SEED'] == str(config.seeds.freesurfer)


def _fake_bs_run(self, cmd):
    subj_dir = Path(self.inputs.subjects_dir) / self.inputs.subject_id / 'mri'
    subj_dir.mkdir(parents=True, exist_ok=True)
    (subj_dir / 'brainstemSsLabels.v13.mgz').write_text('')
    (subj_dir / 'brainstemSsLabels.v13.FSvoxelSpace.mgz').write_text('')
    (subj_dir / 'brainstemSsVolumes.v13.txt').write_text('')
    return 'bs out', 'bs err'


def _fake_wm_run(self, cmd):
    subj_dir = Path(self.inputs.subjects_dir) / self.inputs.subject_id / 'mri'
    subj_dir.mkdir(parents=True, exist_ok=True)
    (subj_dir / 'wmparc.mgz').write_text('')
    return 'wm out', 'wm err'


def test_segmentbs_stdout_stderr(monkeypatch, tmp_path):
    seg = SegmentBS(subjects_dir=str(tmp_path), subject_id='sub-01')
    monkeypatch.setattr(SegmentBS, '_run_command', _fake_bs_run)
    res = seg.run()
    assert res.outputs.stdout == 'bs out'
    assert res.outputs.stderr == 'bs err'


def test_segmentwm_stdout_stderr(monkeypatch, tmp_path):
    seg = SegmentWM(subjects_dir=str(tmp_path), subject_id='sub-01')
    monkeypatch.setattr(SegmentWM, '_run_command', _fake_wm_run)
    res = seg.run()
    assert res.outputs.stdout == 'wm out'
    assert res.outputs.stderr == 'wm err'


def test_set_freesurfer_seed_runtime():
    runtime = SimpleNamespace(environ={})

    runtime = _set_freesurfer_seed(runtime)

    assert runtime.environ['FREESURFER_RANDOM_SEED'] == str(config.seeds.freesurfer)
