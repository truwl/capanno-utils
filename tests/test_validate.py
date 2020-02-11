
from tests.test_base import TestBase
from pathlib import Path
from xd_cwl_utils.helpers.get_paths import get_tool_metadata
from xd_cwl_utils.validate_metadata import metadata_validator_factory
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata


class TestValidateMetadata(TestBase):

    def test_validate_tool_metadata(self):
        # validate_tool_metadata = metadata_validator_factory(ToolMetadata)
        # metadata_path = get_tool_metadata('sort', '8.25')
        # validate_tool_metadata(metadata_path)
        # Todo update.
        return

    def test_validate_tool_metadata_fail(self):
        # validate_tool_metadata = metadata_validator_factory(ToolMetadata)
        # metadata_path = Path().cwd() / 'tests/test_files/bad_gawk-metadata.yaml'
        # with self.assertRaises(ValueError):
        #     validate_tool_metadata(metadata_path)
        # Todo update.
        return

    def test_validate_parent_tool_metadata(self):
        validate_parent_metadata = metadata_validator_factory(ParentToolMetadata)
        metadata_path = get_tool_metadata('STAR', '2.5', parent=True)
        validate_parent_metadata(metadata_path)

    def test_validate_parent_tool_metadata_fail(self):
        validate_parent_metadata = metadata_validator_factory(ParentToolMetadata)
        metadata_path = Path.cwd() / ('tests/test_files/test_content/invalid_content/cwl-tools/cat/8.x/common/common-metadata.yaml')
        with self.assertRaises(AttributeError):
            validate_parent_metadata(metadata_path)
        return

    def test_validate_subtool_metadata(self):
        validate_subtool_metadata = metadata_validator_factory(SubtoolMetadata)
        metadata_path = get_tool_metadata('STAR', '2.5', subtool_name='alignReads')
        validate_subtool_metadata(metadata_path)
        return

    def test_validate_subtool_metadata_fail(self):
        validate_subtool_metadata = metadata_validator_factory(SubtoolMetadata)
        metadata_path = Path.cwd() / 'tests/test_files/test_content/invalid_content/cwl-tools/samtools/1.9/samtools_view/samtools-view-metadata.yaml' # Works for now.  # subtool name not in parent featurelist.
        with self.assertRaises(ValueError):
            validate_subtool_metadata(metadata_path)
        return



