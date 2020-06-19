""" Get projects from https://github.com/common-workflow-library/bio-cwl-tools
    make sure this repo is added as a submodule so we can just parse it locally instead of getting bogged down in scraping
    git submodule add git@github.com:common-workflow-library/bio-cwl-tools.git bio-cwl-tools-submodule
    from xd_cwl_utils.helpers import get_bio_cwl_tools
    get_bio_cwl_tools.listVersion()
"""

import cwl_utils.parser_v1_0 as parser
import os
import re
import sys
import glob
from abc import abstractmethod
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.compat import string_types, ordereddict
import logging, sys
import subprocess
from typing import Optional
from xd_cwl_utils.add.add_tools import add_tool, add_subtool
from xd_cwl_utils.helpers.get_paths import get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, get_tool_dir

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


class repoImporter(object):
    """Import cwl tools and workflows from a third-party repo"""
    def __init__(
            self,
            *,
            path: str,
            name: Optional[str] = None,
            identifier: Optional[str] = None,
            commithash: Optional[str] = None
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

        m = re.search(' ([a-z0-9]+)', str(stdout))
        # TODO: if there are multiple submodules then it won't work
        self.commithash=m[1]

    @abstractmethod
    def getCwlInfos(self) -> None:
        pass

    @abstractmethod
    def getCwlInfo(self, tool: str, subtoolcwl: str) -> dict:
        pass

class bioCwl(repoImporter):
    def __init__(
            self,
            *,
            path: str = "bio-cwl-tools-submodule",
            name: Optional[str] = None,
            identifier: Optional[str] = None
    ) -> None:
        super().__init__(path=path)

    def getCwlInfos(self) -> None:
        logging.info("getCWLinfos")
        tooldict = {}
        #for tool in [os.path.basename(x[1]) for x in os.walk(self.path)]:
        for tool in os.listdir(self.path):
            logging.info("a potential:{}".format(tool))
            if os.path.isdir(os.path.join(self.path,tool)) and not tool.startswith('.'):
                logging.info("going with:{}".format(tool))
                tooldict[tool] = {}
                tooldict[tool]['subtools'] = []

                #TODO: consider using the x[2] from os.walk
                versions_reported = []
                for subtoolcwl in glob.glob(self.path+"/"+tool+'/*cwl'):
                    logging.info("\tsub:{}".format(os.path.basename(subtoolcwl)))
                    subtooldict=self.getCwlInfo(tool,str(os.path.basename(subtoolcwl)))
                    tooldict[tool]['subtools']+=[subtooldict]

                    for k,v in subtooldict.items():
                        logging.info("{}:{}".format(k, v))
                        #can we figure out a consensus for the version?
                        if k=='version':
                            versions_reported+=[v]
                if len(set(versions_reported)) > 1:
                    raise ValueError('Observing multiple versions in the tool {}'.format(tool))
                elif len(versions_reported) == 0:
                    raise ValueError('Observing no versions in the tool {}'.format(tool))
                tooldict[tool]['version']=versions_reported[0]
        logging.info("addtool loop")
        for tool in tooldict.keys():
            if len(tooldict[tool]['subtools'])>1:
                # TODO: has_primary could be true? we need to figure this out
                has_primary = False
                subtoolnames = tooldict[tool]['subtools']
            else:
                has_primary = True
                subtoolnames=main_tool_subtool_name
            # TODO: study the existing tool directory and try not to clobber other versions
            logging.info("adding tool {}".format(tool))
            add_tool(tool, version_name=tooldict[tool]['version'], subtool_names=subtoolnames, biotools_id=tool,
                             has_primary=has_primary) #, init_cwl=args.init_cwl, root_repo_path=args.root_path)
            for subtool in tooldict['tools']['subtools']:
                logging.info("adding subtool {}".format(subtool['name']))
                add_subtool(tool_name=tool, tool_version=subtool['version'], subtool_name=subtool['name'],
                            init_cwl=subtool['subtoolcwl']) #root_repo_path=Path.cwd(),update_featureList=False, init_cwl=subtoolcwl)


    def getCwlInfo(self, tool: str, subtoolcwl: str) -> dict:
        """
        Fetch vital information about a subtool
        :param tool: the tool e.g. bamtools
        :param subtoolcwl: the subtool cwl file e.g. bamtools_stats.cwl
        :return: dict with tool_name, version_name, subtool name
        """
        filename=os.path.join(self.path,tool,subtoolcwl)
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
        name=subtoolcwl.replace('.cwl','')
        return({'name':name,'subtoolcwl':subtoolcwl,'version':version,'docker':docker})
