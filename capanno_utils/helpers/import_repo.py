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


logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class repoImporter(object):
    """Import cwl tools and workflows from a third-party repo"""
    def __init__(
            self,
            *,
            path: str,
            name: Optional[str] = None,
            identifier: Optional[str] = None,
            commithash: Optional[str] = None,
            denylist: Optional[list] = None
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
        self.abspath=os.path.join(os.path.dirname(__file__),"../../",self.path)
        self.name=name
        self.identifier=identifier
        self.commithash = commithash
        self.denylist = denylist
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
            denylist: Optional[list] = ['pca','util','graph-genome-segmentation'] #pca is half-baked, util is just rename, ggs has a Dockerfile but no image
    ) -> None:
        super().__init__(path=path,denylist=denylist)

    def getCwlInfos(self) -> None:
        logger.debug("getCWLinfos")
        tooldict = {}
        #for tool in [os.path.basename(x[1]) for x in os.walk(self.path)]:
        for tool in os.listdir(self.abspath):
            logger.info("potential tool:{}".format(tool))
            logger.debug("potential tool:{}".format(tool))
            if tool not in self.denylist and os.path.isdir(os.path.join(self.path,tool)) and not tool.startswith('.'):
                logger.info("accepted:{}".format(tool))
                tooldict[tool] = {}
                tooldict[tool]['subtools'] = []

                #TODO: consider using the x[2] from os.walk
                versions_reported = []
                dockers_reported = []
                for subtoolcwl in glob.glob(self.path+"/"+tool+'/*cwl'):
                    logger.info("\tsub:{}".format(os.path.basename(subtoolcwl)))
                    subtooldict=self.getCwlInfo(tool,str(os.path.basename(subtoolcwl)))
                    tooldict[tool]['subtools']+=[subtooldict]

                    for k,v in subtooldict.items():
                        logger.info("{}:{}".format(k, v))
                        #can we figure out a consensus for the version?
                        if k=='version' and v is not None:
                            versions_reported+=[v]
                        elif k=='docker' and v is not None:
                            dockers_reported+=[v]


                if len(set(dockers_reported)) > 1:
                    raise ValueError('Observing multiple docker images in the tool {}: {}'.format(tool, dockers_reported))
                elif len(dockers_reported) == 0:
                    raise ValueError('Observing no docker images in the tool {}'.format(tool))
                else:
                    tooldict[tool]['docker'] = dockers_reported[0]

                if len(set(versions_reported)) > 1:
                    raise ValueError(
                        'Observing multiple versions in the tool {}: {}'.format(tool, versions_reported))
                elif len(versions_reported) == 0:
                    logger.info('Observing no versions in the tool {}'.format(tool))

                    # is there a docker version we can use?
                    # quay.io/biocontainers/picard:2.22.2--0
                    m = re.search('(\\S+)/(.+)', tooldict[tool]['docker'])
                    tooldict[tool]['version']=m[2]
                else:
                    tooldict[tool]['version']=versions_reported[0]
        logger.info("addtool loop")
        for tool in tooldict.keys():
            if len(tooldict[tool]['subtools'])>1:
                # TODO: has_primary could be true? we need to figure this out
                has_primary = False
                subtoolnames = tooldict[tool]['subtools']
            else:
                has_primary = True
                subtoolnames=main_tool_subtool_name
            # TODO: study the existing tool directory and try not to clobber other versions
            logger.info("adding tool {}".format(tool))
            add_tool(tool, version_name=tooldict[tool]['version'], subtool_names=subtoolnames, biotools_id=tool,
                             has_primary=has_primary) #, init_cwl=args.init_cwl, root_repo_path=args.root_path)
            for subtool in tooldict['tools']['subtools']:
                logger.info("adding subtool {}".format(subtool['name']))
                add_subtool(tool_name=tool, tool_version=subtool['version'], subtool_name=subtool['name'],init_cwl=subtool['subtoolcwl']) #root_repo_path=Path.cwd(),update_featureList=False, init_cwl=subtoolcwl)


    def getCwlInfo(self, tool: str, subtoolcwl: str) -> dict:
        """
        Fetch vital information about a subtool
        :param tool: the tool e.g. bamtools
        :param subtoolcwl: the subtool cwl basename e.g. bamtools_stats.cwl
        :return: dict with tool_name, version_name, subtool name
        """
        filename=os.path.join(self.abspath,tool,subtoolcwl)
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
                                    logger.info("version:{}".format(version))
                                except KeyError as e:
                                    logger.debug("keyerror:{}".format(e))
                                except IndexError as e:
                                    logger.debug("indexerror:{}".format(e))
                        elif hint['class']=='DockerRequirement':
                            try:
                                docker=hint['dockerPull']
                                logger.debug("docker:{}".format(docker))
                            except KeyError as e:
                                logger.debug("keyerror:{}".format(e))
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
                #result['requirements'].__class__ == ruamel.yaml.comments.CommentedSeq
                for req in result['requirements']:
                    if 'dockerPull' in req:
                        docker=req['dockerPull']
                        logger.debug("direct dockerpull:{}".format(subtoolcwl))
                    #see Lancet
                    # ('requirements', ordereddict([('DockerRequirement', ordereddict([('dockerPull', 'sinaiiidgst/lancet:latest')])), ('InlineJavascriptRequirement', ordereddict())])), ('inputs', ordereddict([('TumorInput', ordereddict([('type', 'File'), ('inputBinding', ordereddict([('prefix', '--tumor')])), ('secondaryFiles', ['.bai'])])), ('NormalInput', ordereddict([('type', 'File'), ('inputBinding', ordereddict([('prefix', '--normal')])), ('secondaryFiles', ['.bai'])])), ('Reference', ordereddict([('type', 'File'), ('format', 'edam:format_1929'), ('inputBinding', ordereddict([('prefix', '--ref')]))])), ('GenomicRegion', ordereddict([('type', ['null', ordereddict([('type', 'record'), ('name', 'GenomicRegion'), ('fields', ordereddict([('Chromosome', ordereddict([('type', 'string')])), ('RegionStart', ordereddict([('type', 'int')])), ('RegionEnd', ordereddict([('type', 'int')])), ('GenomicRegion', ordereddict([('type', 'string'), ('inputBinding', ordereddict([('prefix', '--reg'), ('valueFrom', '$(inputs.GenomicRegion.Chromosome + ":" + inputs.GenomicRegion.RegionStart + "-" + inputs.GenomicRegion.RegionEnd)')]))]))]))])])])), ('BedFile', ordereddict([('type', 'File?'), ('inputBinding', ordereddict([('prefix', '--bed')]))])), ('MinKmer', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-k')]))])), ('MaxKmer', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-k')]))])), ('TrimLowQuality', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--trim-lowqual')]))])), ('MinBaseQual', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-base-qual')]))])), ('QualityRange', ordereddict([('type', 'string?'), ('inputBinding', ordereddict([('prefix', '--quality-range')]))])), ('MinMapQual', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-map-qual')]))])), ('ASXSDifMax', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-as-xs-diff')]))])), ('MaxTipLen', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--tip-len')]))])), ('MinCovThres', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--cov-thr')]))])), ('MinCovRatio', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--cov-ratio')]))])), ('LowCovThres', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--low-cov')]))])), ('MaxAvgCov', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-avg-cov')]))])), ('WinSize', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--window-size')]))])), ('Padding', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--padding')]))])), ('DFSLimit', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--dfs-limit')]))])), ('MaxIndelLen', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-inde-len')]))])), ('MaxMismatch', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-mismatch')]))])), ('Threads', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--num-threads')]))])), ('NodeStrLen', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--node-str-len')]))])), ('MinAltCountTumor', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-alt-count-tumor')]))])), ('MaxAltCountNormal', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-alt-count-normal')]))])), ('MinVAFTumor', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--min-vaf-tumor')]))])), ('MaxVAFNormal', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--max-vaf-normal')]))])), ('MinCovTumor', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-coverage-tumor')]))])), ('MaxCovTumor', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-coverage-tumor')]))])), ('MinCovNormal', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-coverage-normal')]))])), ('MaxCovNormal', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-coverage-normal')]))])), ('MinPhredFisher', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--min-phred-fisher')]))])), ('MinPhredFisherSTR', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--min-phred-fisher-str')]))])), ('MinStrandBias', ordereddict([('type', 'float?'), ('inputBinding', ordereddict([('prefix', '--min-strand-bias')]))])), ('MaxUnitLen', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--max-unit-length')]))])), ('MinReportUnit', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-report-unit')]))])), ('MinReportLen', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--min-report-len')]))])), ('DistFrSTR', ordereddict([('type', 'int?'), ('inputBinding', ordereddict([('prefix', '--dist-from-str')]))])), ('ActRegOff', ordereddict([('type', 'boolean?'), ('inputBinding', ordereddict([('prefix', '--active-region-off')]))])), ('KmerRecov', ordereddict([('type', 'boolean?'), ('inputBinding', ordereddict([('prefix', '--kmer-recovery')]))])), ('PrintGraph', ordereddict([('type', 'boolean?'), ('inputBinding', ordereddict([('prefix', '--print-graph')]))])), ('Verbose', ordereddict([('type', 'boolean?'), ('inputBinding', ordereddict([('prefix', '--verbose')]))]))])), ('baseCommand', 'lancet'), ('outputs', ordereddict([('vcf', ordereddict([('format', 'edam:format_3016'), ('type', 'stdout')]))])), ('stdout', 'lancet-out.vcf'), ('$namespaces', ordereddict([('edam', 'http://edamontology.org/')])), ('$schemas', ['http://edamontology.org/EDAM_1.18.owl'])])
                    if 'DockerRequirement' in req:
                        logger.debug("dockerrequirement.dockerpull dockerpull:{}".format(subtoolcwl))
                        docker=result['requirements']['DockerRequirement']['dockerPull']

        name=subtoolcwl.replace('.cwl','')
        if not all([name, subtoolcwl, version, docker]):
            raise Exception('missing one of name:{} cwl:{} version:{} docker:{}'.format(name,subtoolcwl,version,docker))
        return({'name':name,'subtoolcwl':subtoolcwl,'version':version,'docker':docker})