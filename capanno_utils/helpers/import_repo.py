""" Get projects from https://github.com/common-workflow-library/bio-cwl-tools
    make sure this repo is added as a submodule so we can just parse it locally instead of getting bogged down in scraping
    git submodule add git@github.com:common-workflow-library/bio-cwl-tools.git bio-cwl-tools-submodule
    from capanno_utils.helpers.import_repo import bioCwl;mybiocwl=bioCwl();mybiocwl.processDir()
"""

#import cwl_utils.parser_v1_0 as parser
from capanno_utils.classes.cwl import common_workflow_language as pycwl
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
from capanno_utils.add.add_tools import add_tool, add_subtool
from capanno_utils.helpers.get_paths import get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, get_tool_dir
from capanno_utils.helpers.get_paths import get_tool_sources, get_cwl_script, main_tool_subtool_name
from capanno_utils.classes.cwl.common_workflow_language import load_document

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

class bioSnakemakeWrappers(repoImporter):
    def __init__(
            self,
            *,
            path: str = "snakemake-wrappers/bio",
            denylist: Optional[list] = []
    ) -> None:
        super().__init__(path=path,denylist=denylist)

    def processDir(self) -> None:
        logger.debug("processDir")
        #for tool in [os.path.basename(x[1]) for x in os.walk(self.path)]:
        for tool in os.listdir(self.abspath):
            logger.info("potential tool:{}".format(tool))
            logger.debug("potential tool:{}".format(tool))
            if tool not in self.denylist and os.path.isdir(os.path.join(self.path,tool)) and not tool.startswith('.'):
                logger.info("accepted:{}".format(tool))
                self.processTool(tool)

    def processTool(self, tool, addSubtoolsToTool=True, no_clobber=True) -> None:
        tooldict = {}
        tooldict[tool] = {}
        tooldict[tool]['subtools'] = []

        #TODO: consider using the x[2] from os.walk
        versions_reported = []
        dockers_reported = []
        biotools_reported = []
        for subtoolsource in glob.glob(self.path+"/"+tool+'/wrapper.py'):
            if os.path.basename(subtoolsource) not in self.denylist:
                logger.info("\tsub:{}".format(os.path.basename(subtoolsource)))
                subtooldict=self.getSMWrapInfo(tool,str(os.path.join(os.path.basename(subtoolsource),))
                tooldict[tool]['subtools']+=[subtoolsource]

                for k,v in subtooldict.items():
                    logger.info("{}:{}".format(k, v))
                    #can we figure out a consensus for the version?
                    if k=='version' and v is not None:
                        versions_reported+=[v]
                    elif k=='docker' and v is not None:
                        dockers_reported+=[v]
                    elif k=='biotools' and v is not None:
                        biotools_reported+=[v]


        if len(set(dockers_reported)) > 1:
            logger.error('Observing multiple docker images in the tool {}: {}'.format(tool, dockers_reported))
            tooldict[tool]['docker'] = dockers_reported[0]
        elif len(dockers_reported) == 0:
            logger.error('Observing no docker images in the tool {}'.format(tool))
        else:
            tooldict[tool]['docker'] = dockers_reported[0]

        if len(set(versions_reported)) > 1:
            logger.error(
                'Observing multiple versions in the tool {}: {}'.format(tool, versions_reported))
        elif len(versions_reported) == 0:
            logger.info('Observing no versions in the tool {}'.format(tool))

        if len(set(biotools_reported)) >= 1:
            tooldict[tool]['biotools'] = biotools_reported[0]
        else:
            tooldict[tool]['biotools'] = None

        # is there a docker version we can use?
        # quay.io/biocontainers/picard:2.22.2--0 should really be 2.22.2
        if len(dockers_reported) > 0:
            m = re.search('(\\S+):v?([.0-9]+)', tooldict[tool]['docker'])
            if m is not None:
                tooldict[tool]['version']=m[2]
                versions_reported+=[m[2]]
        #else:
        #    tooldict[tool]['version']=versions_reported[0]

        if len(versions_reported) == 0:
            raise RuntimeError("Can't find version for {}".format(tool))
        else:
            tooldict[tool]['version'] = versions_reported[0]
        logger.info("addtool loop")
        for tool in tooldict.keys():
            subtoolnames = []
            if len(tooldict[tool]['subtools'])>1:
                # TODO: has_primary could be true? we need to figure this out
                has_primary = False
                for subtool in tooldict[tool]['subtools']:
                    subtoolnames += [subtool['name']]
            else:
                has_primary = True
                subtoolnames=main_tool_subtool_name
            # TODO: study the existing tool directory and try not to clobber other versions
            logger.info("adding tool: {} version: {} biotools: {} subtoolnames: {}".format(tool,tooldict[tool]['version'],tooldict[tool]['biotools'],subtoolnames))
            if addSubtoolsToTool:
                add_tool(tool, version_name=tooldict[tool]['version'],subtool_names=[],biotools_id=tooldict[tool]['biotools'], no_clobber = no_clobber)
            else:
                add_tool(tool, version_name=tooldict[tool]['version'], subtool_names=subtoolnames, biotools_id=tooldict[tool]['biotools'],
                                 has_primary=has_primary, init_cwl = False, no_clobber = no_clobber) #, init_cwl=args.init_cwl, root_repo_path=args.root_path)
            #add_tool visits the subtools
            if addSubtoolsToTool:
                for subtool in tooldict[tool]['subtools']:
                    logger.info("adding subtool {}".format(subtool['name']))
                    #add_content_main(['-p', tmp_dir, 'subtool', tool_name, tool_version, subtool_name, '-u', '--init-cwl', cwl_url])

                    #bio-cwl tools has the habit of naming tools like picard_MarkDuplicates.cwl
                    if subtool['name'].startswith(tool):
                        subtool_name = subtool['name'].replace(tool+'_','')
                    else:
                        subtool_name = subtool['name']

                    if subtool['version'] is None:
                        tool_version = tooldict[tool]['version']
                    else:
                        tool_version = subtool['version']
                    logger.info("adding subtool: {} version: {} path: {}".format(subtool_name, subtool['version'],
                                                                                 subtool['path']))
                    add_subtool(tool_name=tool, tool_version=tool_version, subtool_name=subtool_name,init_cwl=subtool['path'], update_featureList=True, no_clobber = no_clobber) #root_repo_path=Path.cwd(),update_featureList=False, init_cwl=subtoolcwl)


    def getCwlInfo(self, tool: str, subtoolcwl: str, acceptClassYaml = False) -> dict:
        """
        Fetch vital information about a subtool
        :param tool: the tool e.g. bamtools
        :param subtoolcwl: the subtool cwl basename e.g. bamtools_stats.cwl
        :param acceptClassYaml: allow -class style descriptors
        :return: dict with tool_name, version_name, subtool name
        """
        filename=os.path.join(self.abspath,tool,subtoolcwl)
        version = docker = biotools = None
        with open(filename) as fp:
            result = ruamel.yaml.main.round_trip_load(fp)
            #result_pycwl = pycwl.load_document(fp)
            if 'hints' in result:
                sftreq = None


                for hintkey in result['hints']: # hintkey = ordereddict([('class', 'DockerRequirement'), ('dockerPull', 'quay.io/biocontainers/picard:2.22.2--0')])
                    if 'class' in hintkey:
                        if not acceptClassYaml:
                            raise ValueError("No -class style Yaml accepted for tool info {} {}".format(tool, subtoolcwl))
                        if hintkey['class']=='SoftwareRequirement':
                            sftreq = hintkey['packages']
                        elif hintkey['class'] == 'DockerRequirement':
                            try:
                                docker = hintkey['dockerPull']
                                logger.debug("docker:{}".format(docker))
                            except KeyError as e:
                                logger.debug("keyerror:{}".format(e))
                    elif hintkey == 'SoftwareRequirement':
                        sftreq = result['hints']['SoftwareRequirement']['packages'][tool]
                    elif hintkey == 'DockerRequirement':
                        # see picard_AddOrReplaceReadGroups
                        # import pdb
                        # pdb.set_trace()
                        if 'dockerPull' in result['hints']['DockerRequirement']:
                            docker = result['hints']['DockerRequirement']['dockerPull']
                        else:
                            # graph-genome-segmentation component_segmentation.cwl
                            docker = result['hints']['DockerRequirement']['dockerFile']
                    if sftreq is not None:
                        logger.info("SoftwareRequirement found")
                        try:
                            version=result['hints']['SoftwareRequirement']['packages'][tool]['version'][0]
                            logger.info("version:{}".format(version))
                        except KeyError as e:
                            logger.debug("keyerror:{}".format(e))
                        except IndexError as e:
                            logger.debug("indexerror:{}".format(e))
                        try:
                            specs=result['hints']['SoftwareRequirement']['packages'][tool]['specs'][0]
                            if 'biotools' in specs or 'bio.tools' in specs:
                                #http://identifiers.org/biotools/gatk
                                #https://bio.tools/picard_arrg
                                m = re.search('bio.?tools/(.+)', specs)
                                biotools = m[1]
                        except KeyError as e:
                            logger.debug("keyerror:{}".format(e))
                        except IndexError as e:
                            logger.debug("indexerror:{}".format(e))
            if 'requirements' in result:
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
        if not all([name, subtoolcwl, version, docker, biotools]):
            logger.error('missing one of name:{} cwl:{} version:{} docker:{} biotools:{}'.format(name,subtoolcwl,version,docker,biotools))
            #raise Exception('missing one of name:{} cwl:{} version:{} docker:{}'.format(name,subtoolcwl,version,docker))
        return({'name':name,'basename':subtoolcwl,'path':filename,'version':version,'docker':docker,'biotools':biotools})
