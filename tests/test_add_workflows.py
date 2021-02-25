from tempfile import TemporaryDirectory
from tests.test_base import TestBase
from capanno_utils.add.add_workflows import add_workflow

class TestAddWorkflow(TestBase):

    def test_add_workflow(self):
        workflow_group_name = 'test_group'
        workflow_name = 'test_workflow'
        workflow_version = '0.1.1'
        with TemporaryDirectory(prefix='test_add_workflow') as tmp_dir:
            add_workflow(workflow_group_name, workflow_name, workflow_version, root_repo_path=tmp_dir)
            assert True
        return