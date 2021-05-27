import os
import tempfile
from tests.test_base import TestBase
from capanno_utils.repo_config import config
from capanno_utils.content_maps import make_tools_map_dict, make_script_maps
from capanno_utils.status import update_existing_tool_wrapper_status, update_all_tools_to_released


class TestChangeStatus(TestBase):

    def test_update_existing_files_to_released(self):
        tool_map_item = {
            'metadataPath': 'tools/samtools/1.x/samtools_idxstats/samtools-idxstats-metadata.yaml',
            'name': 'idxstats',
            'metadataStatus': 'Released',
            'cwlStatus': 'Incomplete',
            'cwlExists': False,
            'nextflowStatus': 'Incomplete',
            'nextflowExists': False,
            'snakemakeStatus': 'Incomplete',
            'snakemakeExists': True,
            'wdlStatus': 'Incomplete',
            'wdlExists': False,
            'type': 'subtool'} #'TL_ec2a8d_d1.0b'
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_dir(tmp_dir)
            self.make_empty_tools_index(tmp_dir)
            update_existing_tool_wrapper_status(tool_map_item, base_dir=self.src_content_dir, update_dir=tmp_dir)
            assert True
        return

    def test_update_all(self):
        """Update all workflow files that exist to released. Make changes in update_dir to keep original unchanged."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.copy_all_content_repo_tools(tmp_dir)
            update_all_tools_to_released(base_dir=self.src_content_dir, update_dir=tmp_dir)
            assert True
        return
