
from tempfile import TemporaryDirectory
from tests.test_base import TestBase, test_constants
from capanno_utils.add_content import main as add_content
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata, ToolInstanceMetadata
from capanno_utils.helpers.get_paths import get_tool_metadata, get_tool_instance_metadata_path


class TestMakeToolInstanceMetadata(TestBase):

    test_instance_dict = {'name': 'test tool instance  1', 'toolIdentifier': 'TL_aaaaaa_aa.aa', 'description': 'Test description loaded from a dict.'}

    def test_make_tool_instance_metadata(self):
        tool_instance_meta = ToolInstanceMetadata(**TestMakeToolInstanceMetadata.test_instance_dict)
        return

    def test_make_tool_instance_metadata_from_subtool(self):
        p_metadata = ParentToolMetadata(name='parentName',
                                        softwareVersion=test_constants['test_software_version'],
                                        featureList=['subtool_name'])
        st_metadata = SubtoolMetadata(name='subtool_name', _parentMetadata=p_metadata)
        instance_metadata = st_metadata.mk_instance()
        return

    def test_make_file(self):
        parent_tool_name = 'parentName'
        subtool_name = 'subtoolName'
        tool_version = 'test_version'
        # st_metadata = SubtoolMetadata(name=subtool_name, _parentMetadata=p_metadata)
        # instance_metadata = st_metadata.mk_instance()
        with TemporaryDirectory(prefix='tool_instance_metadata') as tmpdir:
            add_content(['-p', tmpdir, 'tool', parent_tool_name, tool_version, subtool_name])
            subtool_path = get_tool_metadata(parent_tool_name, tool_version, subtool_name, base_dir=tmpdir)
            subtool_metadata = SubtoolMetadata.load_from_file(subtool_path)
            subtool_instance = subtool_metadata.mk_instance()
            subtool_instance.mk_file(base_dir=tmpdir)
        return

    def test_load_from_file(self):
        instance_file_args = {'tool_name': 'gawk', 'tool_version': '4.1.x', 'input_hash': '1c10', 'base_dir': self.test_content_dir}
        instance_metadata_path = get_tool_instance_metadata_path(**instance_file_args)
        tool_instance = ToolInstanceMetadata.load_from_file(instance_metadata_path)
        return