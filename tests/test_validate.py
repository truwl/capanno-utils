
from tests.test_base import TestBase
from pathlib import Path
from xd_cwl_utils.helpers.get_paths import get_cwl_tool_metadata
from xd_cwl_utils.validate_metadata import metadata_validator_factory
from xd_cwl_utils.classes.metadata.tool_metadata import ToolMetadata, ParentToolMetadata, SubtoolMetadata


class TestValidateMetadata(TestBase):

    def test_validate_tool_metadata(self):
        validate_tool_metadata = metadata_validator_factory(ToolMetadata)
        metadata_path = get_cwl_tool_metadata('sort', '8.25')
        validate_tool_metadata(metadata_path)
        return

    def test_validate_tool_metadata_fail(self):
        validate_tool_metadata = metadata_validator_factory(ToolMetadata)
        metadata_path = Path().cwd() / 'tests/test_files/bad_gawk-metadata.yaml'
        with self.assertRaises(ValueError):
            validate_tool_metadata(metadata_path)
        return

    def test_validate_parent_tool_metadata(self):
        validate_parent_metadata = metadata_validator_factory(ParentToolMetadata)
        metadata_path = get_cwl_tool_metadata('STAR', '2.5', parent=True)
        validate_parent_metadata(metadata_path)

    def test_validate_parent_tool_metadata_fail(self):
        validate_parent_metadata = metadata_validator_factory(ParentToolMetadata)
        metadata_path = Path.cwd() / ('tests/test_files/test_content/cwl_tools_bad/samtools/1.3/common/bad_samtools-metadata.yaml')
        with self.assertRaises(AttributeError):
            validate_parent_metadata(metadata_path)
        return

    def test_validate_subtool_metadata(self):
        validate_subtool_metadata = metadata_validator_factory(SubtoolMetadata)
        metadata_path = get_cwl_tool_metadata('STAR', '2.5', subtool_name='alignReads')
        validate_subtool_metadata(metadata_path)
        return

    def test_validate_subtool_metadata_fail(self):
        validate_subtool_metadata = metadata_validator_factory(SubtoolMetadata)
        metadata_path = Path.cwd() / 'tests/test_files/test_content/cwl_tools_bad/samtools/1.3/samtools_notRight/samtools-notRight-metadata.yaml'  # subtool name not in parent featurelist.
        with self.assertRaises(ValueError):
            validate_subtool_metadata(metadata_path)
        return



