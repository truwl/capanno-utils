""" Get projects from https://github.com/common-workflow-library/bio-cwl-tools
    make sure this repo is added as a submodule so we can just parse it locally instead of getting bogged down in scraping
    git submodule add git@github.com:common-workflow-library/bio-cwl-tools.git bio-cwl-tools-submodule
    from xd_cwl_utils.helpers import get_bio_cwl_tools
    get_bio_cwl_tools.listVersion()
"""

import cwl_utils.parser_v1_0 as parser
import os
import sys
import glob
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.compat import string_types, ordereddict
import logging, sys
import subprocess
from typing import Optional
from xd_cwl_utils.add.add_tools import add_tool, add_subtool

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)


class repoImporter(object):
    """Import cwl tools and workflows from a third-party repo"""
    def __init__(
            self,
            *,
            path: str,
            name: Optional[str] = None,
            identifier: Optional[str] = None
    ) -> None:
        """Create some generic repoImporter object
        :param path: local path to the repo (usually a git subclone e.g. bio-cwl-tools-submodule)
        :param name: name of this import ("July_refresh")
        """

        #import the git info
        #git submodule
        #61ffac1862822f08dc20b6f8e2f22634b986b0bc bio-cwl-tools-submodule (heads/release)

        #this might be hard to parse consistently
        #git submodule foreach 'git remote show origin'
        # Entering 'bio-cwl-tools-submodule'
        # * remote origin
        #   Fetch URL: git@github.com:common-workflow-library/bio-cwl-tools.git
        #   Push  URL: git@github.com:common-workflow-library/bio-cwl-tools.git
        self.path=path
        self.name=name
        self.identifier=identifier

        process = subprocess.Popen(['git', 'submodule'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout, stderr)

    def getCwlInfos(self):
        pass

    def getCwlInfo(self):
        pass

class bioCwl(repoImporter):
    def __init__(
            self,
            *,
            path: str = "bio-cwl-tools-submodule",
            name: Optional[str] = None,
            identifier: Optional[str] = None
    ) -> None:
        super().__init__()

    def getCwlInfos(self):
        for tool in [os.path.basename(x[0]) for x in os.walk(self.path)]:
            logging.info(tool)
            #TODO: consider using the x[2] from os.walk
            for subtoolcwl in glob.glob(self.path+"/"+tool+'/*cwl'):
                logging.info("\t{}".format(os.path.basename(subtoolcwl)))
                res=self.getBioCwlInfo(self.path,tool,os.path.basename(subtoolcwl))
                for k,v in res.items():
                    print("{}:{}".format(k, v))
                    #add_tool(args.tool_name, args.version_name, subtool_names=args.subtool_names, biotools_id=args.biotoolsID, has_primary=args.has_primary, init_cwl=args.init_cwl,root_repo_path=args.root_path)


    def getCwlInfo(biocwltoolspath="bio-cwl-tools-submodule",tool="bamtools",subtoolcwl="bamtools_stats.cwl"):
        filename=os.path.join(biocwltoolspath,tool,subtoolcwl)
        version = docker = None
        with open(filename) as fp:
            result = ruamel.yaml.main.round_trip_load(fp)

            if 'hints' in result:
                for hint in result['hints']:
                    if 'class' in hint:
                        if hint['class']=='SoftwareRequirement':
                            if 'packages' in hint:
                                try:
                                    version=hint['packages'][tool]['version'][0]
                                    logging.info("version:{}".format(version))
                                except KeyError as e:
                                    logging.debug("keyerror:{}".format(e))
                                except IndexError as e:
                                    logging.debug("indexerror:{}".format(e))
                        elif hint['class']=='DockerRequirement':
                            try:
                                docker=hint['dockerPull']
                                logging.debug("docker:{}".format(docker))
                            except KeyError as e:
                                logging.debug("keyerror:{}".format(e))
                    elif 'DockerRequirement' in hint:
                        #see picard_AddOrReplaceReadGroups
                        # import pdb
                        # pdb.set_trace()
                        if 'dockerPull' in result['hints']['DockerRequirement']:
                            docker=result['hints']['DockerRequirement']['dockerPull']
                        else:
                            #graph-genome-segmentation component_segmentation.cwl
                            docker=result['hints']['DockerRequirement']['dockerFile']
            if 'requirements' in result:
                for req in result['requirements']:
                    if 'dockerPull' in req:
                        docker=req['dockerPull']
        return({'version':version,'docker':docker})
