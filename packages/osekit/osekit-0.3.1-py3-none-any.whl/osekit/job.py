import glob
import json
import os
import subprocess
import time
from collections import namedtuple
from copy import copy
from datetime import datetime
from importlib import resources
from pathlib import Path
from string import Template
from typing import Literal, NamedTuple
from warnings import warn

import tomlkit

from osekit.config import DPDEFAULT, FPDEFAULT
from osekit.utils.core_utils import chmod_if_needed, read_config

JOB_CONFIG_TEMPLATE = namedtuple(
    "job_config",
    [
        "job_scheduler",
        "env_script",
        "env_name",
        "queue",
        "nodes",
        "walltime",
        "ncpus",
        "mem",
        "outfile",
        "errfile",
    ],
)


class Job_builder:
    def __init__(self, config_file: str = None, nb_jobs: int = 1):
        if config_file is None:
            self.__configfile = "config.toml"
            self.__full_config: NamedTuple = read_config(
                resources.files("osekit").joinpath(self.__configfile),
            )

        else:
            self.__configfile = config_file
            self.__full_config: NamedTuple = read_config(config_file)

        self.__config = self.__full_config["Job"]

        self.__prepared_jobs = []
        self.__ongoing_jobs = []
        self.__finished_jobs = []
        self.__cancelled_jobs = []

        self.nb_jobs = nb_jobs

        required_properties = [
            "job_scheduler",
            "env_script",
            "env_name",
            "queue",
            "nodes",
            "walltime",
            "ncpus",
            "mem",
            "outfile",
            "errfile",
        ]

        if not all(prop in self.__config.keys() for prop in required_properties):
            raise ValueError(
                f"The provided configuration file is missing the following attributes: {'; '.join(list(set(required_properties).difference(set(self.__config._fields))))}",
            )

    # region Properties
    # READ-ONLY properties
    @property
    def config(self) -> dict:
        return self.__config

    @property
    def prepared_jobs(self):
        return self.__prepared_jobs

    @property
    def ongoing_jobs(self):
        self.update_job_status()
        return self.__ongoing_jobs

    @property
    def finished_jobs(self):
        self.update_job_status()
        return self.__finished_jobs

    @property
    def cancelled_jobs(self):
        return self.__cancelled_jobs

    @property
    def all_jobs(self):
        return (
            self.prepared_jobs
            + self.ongoing_jobs
            + self.finished_jobs
            + self.cancelled_jobs
        )

    # READ-WRITE properties
    @property
    def job_scheduler(self):
        return self.__config["job_scheduler"]

    @job_scheduler.setter
    def job_Scheduler(self, value: Literal["Torque", "Slurm"]):
        self.__config = self.__config["job_scheduler"] = value

    @property
    def env_script(self):
        return self.__config["env_script"]

    @env_script.setter
    def env_script(self, value):
        self.__config = self.__config["env_script"] = value

    @property
    def env_name(self):
        return self.__config["env_name"]

    @env_name.setter
    def env_name(self, value):
        self.__config = self.__config["env_name"] = value

    @property
    def queue(self):
        return self.__config["queue"]

    @queue.setter
    def queue(self, value):
        self.__config = self.__config["queue"] = value

    @property
    def nodes(self):
        return self.__config["nodes"]

    @nodes.setter
    def nodes(self, value):
        self.__config = self.__config["nodes"] = value

    @property
    def walltime(self):
        return self.__config["walltime"]

    @walltime.setter
    def walltime(self, value):
        self.__config = self.__config["walltime"] = value

    @property
    def ncpus(self):
        return self.__config["ncpus"]

    @ncpus.setter
    def ncpus(self, value):
        self.__config = self.__config["ncpus"] = value

    @property
    def mem(self):
        return self.__config["mem"]

    @mem.setter
    def mem(self, value):
        self.__config = self.__config["mem"] = value

    @property
    def outfile(self):
        return self.__config["outfile"]

    @outfile.setter
    def outfile(self, value):
        self.__config = self.__config["outfile"] = value

    @property
    def errfile(self):
        return self.__config["errfile"]

    @errfile.setter
    def errfile(self, value):
        self.__config = self.__config["errfile"] = value

    # endregion

    # TODO: Move to utils
    def write_configuration(self, output_file: str = None):
        """Writes the configuration to the original configuration file, or a new file if specified.

        Parameter
        ---------
            `output_file`: the path to the new configuration file (in TOML or JSON format).
        """
        output_format = (
            Path(output_file).suffix if output_file else Path(self.__configfile).suffix
        )

        match output_format:
            case "toml":
                with open(self.__configfile, "w") as outfile:
                    outfile.write(tomlkit.dumps(self.__full_config))
            case "json":
                with open(self.__configfile, "w") as outfile:
                    outfile.write(json.dumps(self.__full_config))

    def build_job_file(
        self,
        *,
        script_path: str,
        script_args: str,
        logdir: Path,
        jobname: str = None,
        preset: Literal["low", "medium", "high"] = None,
        job_scheduler: Literal["Torque", "Slurm"] = None,
        env_script: str = None,
        env_name: str = None,
        queue: str = None,
        nodes: int = None,
        walltime: str = None,
        ncpus: int = None,
        mem: str = None,
        outfile: str = None,
        errfile: str = None,
    ) -> str:
        """Build a job file corresponding to your job scheduler.

        When a job file is created, it becomes a `prepared_job` and can be launched automatically using the `submit_job()` method
        with no arguments.

        This method can use the configuration file to set default job parameters. Use presets to quickly adjust the resource
        consumption or fill the parameters. If a parameter is left empty, it will fall back to the value in the configuration file.
        The default preset is `low` in order to save as much resource as possible.

        Parameters
        ----------
        script_path : `str`, keyword-only
            The path to the script that will be executed in the cluster job
        script_args : `str`, keyword-only
            All the arguments required by the script, as one string.
        jobname : `str`, optional, keyword-only
            The name of the job as seen on the job list (qstat, squeue, ...). The default is the script name.
        preset : `{"low", "medium", "high"}`, optional, keyword-only
            Resource preset for the job. It is best to set up the presets in the configuration file before using them,
            as the default might not correspond to your structure. The default is `low`.
        job_scheduler : `{"Torque", "Slurm"}`, optional, keyword-only
            The job scheduler to which the jobs will be submitted. As of now, only Torque (PBS) and Slurm (Sbatch) are supported.
        env_script : `str`, optional, keyword-only
            The script used to activate the conda environment. If there is no particular script, it can just be `source` or `conda activate`
        env_name : `str`, optional, keyword-only
            The name of the conda environment this job should run into.
        queue : `str`, optional, keyword-only
            The partition/queue/qol in which the job should run. It is very dependant on the cluster.
        nodes : `int`, optional, keyword-only
            The number of nodes (i.e. computers) this job will use. If it is not using a protocol like MPI or an adapted job scheduler (like PEGASUS),
            using more than one node will have no effect.
        walltime : `str`, optional, keyword-only
            The time limit of the job. If exceeded, the job will be killed by the job scheduler. It is best to view large and ask for 1.5 or 2 times
            more than the anticipated time of the job, especially for tasks with a high degree ofo variability in processing time.
        ncpus : `int`, optional, keyword-only
            The number of CPUs required per node.
        mem : `str`, optional, keyword-only
            The quantity of RAM required per CPU. Most of the time it is an integer followed by a G for Gigabytes or Mb for Megabytes.
        outfile : `str`, optional, keyword-only
            The name of the main log file which will record the standard output from the job. If only the name is provided, it will be created in the current
            directory.
        errfile : `str`, optional, keyword-only
            The name of the error log file which will record the error output from the job. If only the name is provided, it will be created in the
            current directory. If there is no error output, it will not be created.

        Returns
        -------
        job_path : `str`
            The path to the created job file.

        """
        if "Presets" in self.__config.keys():
            if preset and preset.lower() not in self.__config["Presets"].keys():
                raise ValueError(
                    f"Unrecognized preset {preset}. Valid presets are: {', '.join(self.__config['Presets'].keys())}",
                )

            job_preset = self.__config["Presets"][preset]
        else:
            preset = None

        logdir.mkdir(mode=DPDEFAULT, exist_ok=True)

        job_file = ["#!/bin/bash"]

        date_id = datetime.now().strftime("%H-%M-%S")
        # region Build header
        #! HEADER
        # Getting all header variables from the parameters or the configuration defaults
        if not job_scheduler:
            job_scheduler = self.job_scheduler
        if not jobname:
            jobname = Path(script_path).name
        if not env_name:
            env_name = self.env_name

        if not outfile:
            outfile = self.outfile

        outfile = logdir.joinpath(outfile)
        if not errfile:
            errfile = self.errfile
        errfile = logdir.joinpath(errfile)

        if not queue:
            queue = self.queue if not preset else job_preset["queue"]
        if not nodes:
            nodes = self.nodes if not preset else job_preset["nodes"]
        if not walltime:
            walltime = self.walltime if not preset else job_preset["walltime"]
        if not ncpus:
            ncpus = self.ncpus if not preset else job_preset["ncpus"]
        if not mem:
            mem = self.mem if not preset else job_preset["mem"]

        match job_scheduler:
            case "Torque":
                prefix = "#PBS"
                name_param = "-N "
                queue_param = "-q "
                node_param = "-l nodes="
                cpu_param = "-l ncpus="
                time_param = "-l walltime="
                mem_param = "-l mem="
                outfile_param = "-o "
                errfile_param = "-e "
                outfile = str(outfile).replace("_%j", "").format(jobname)
                errfile = str(errfile).replace("_%j", "").format(jobname)
            case "Slurm":
                prefix = "#SBATCH"
                name_param = "-J "
                queue_param = "-p "
                node_param = "-n "
                cpu_param = "-c "
                time_param = "-time "
                mem_param = "-mem "
                outfile_param = "-o "
                errfile_param = "-e "
                outfile = str(outfile).format(jobname)
                errfile = str(errfile).format(jobname)
            case _:
                prefix = "#"
                name_param = ""
                queue_param = ""
                node_param = ""
                cpu_param = ""
                time_param = ""
                mem_param = ""
                outfile_param = ""
                errfile_param = ""
                warn(
                    "Unrecognized job scheduler. Please review the PBS file and or specify a job scheduler between Torque or Slurm",
                )

        job_file.append(f"{prefix} {name_param}{jobname}")
        job_file.append(f"{prefix} {queue_param}{queue}")
        job_file.append(f"{prefix} {node_param}{nodes}")
        job_file.append(f"{prefix} {cpu_param}{ncpus}")
        job_file.append(f"{prefix} {time_param}{walltime}")
        job_file.append(f"{prefix} {mem_param}{mem}")

        uid = date_id + str(
            len(glob.glob(Path(outfile).stem[:-2] + "*.out"))
            + len(self.prepared_jobs)
            + len(self.ongoing_jobs),
        ).zfill(3)

        outfile = Path(outfile).with_stem(f"{Path(outfile).stem}{uid}")

        job_file.append(f"{prefix} {outfile_param}{outfile}")
        errfile = Path(errfile).with_stem(f"{Path(errfile).stem}{uid}")
        job_file.append(f"{prefix} {errfile_param}{errfile}")
        # endregion

        job_file.append(f"rm -f {outfile} {errfile}")

        #! ENV
        # The env_script should contain all the command(s) needed to load the script, with the $env_name template where the environment name should be.
        job_file.append(
            Template(f"\n{env_script if env_script else self.env_script}").substitute(
                env_name=env_name,
            ),
        )

        #! SCRIPT
        job_file.append(f"python {script_path} {script_args}")

        #! FOOTER
        outfilename = (
            f"{jobname}_{date_id}_{job_scheduler}_{len(os.listdir(logdir))}.pbs"
        )

        job_file_path = logdir.joinpath(outfilename)
        job_file.append(f"\nrm {job_file_path}\n")

        #! BUILD DONE => WRITING
        with open(job_file_path, "w") as jobfile:
            jobfile.write("\n".join(job_file))

        try:
            get_dict_index_in_list(self.all_jobs, "job_name", jobname)
            jobname = jobname + str(len(self.all_jobs))
        except ValueError:
            pass

        job_info = {
            "job_name": jobname,
            "path": job_file_path,
            "outfile": outfile,
            "errfile": errfile,
        }

        self.__prepared_jobs.append(job_info)

        return job_file_path

    # TODO support multiple dependencies and job chaining (?)
    def submit_job(
        self,
        jobfile: str = None,
        dependency: str | list[str] = None,
    ) -> list[str]:
        """Submits the job file to the cluster using the job scheduler written in the file name or in the configuration file.

        Parameters
        ----------
            jobfile: `str`
                The absolute path of the job file to be submitted. If none is provided, all the prepared job files will be submitted.

            dependency: `str` or `list(str)`
                The job ID this job is dependent on. The afterok:dependency will be added to the command for all jobs submitted.

        Returns
        -------
            A list containing the job ids of the submitted jobs.

        """
        jobinfo_list = (
            [{"path": jobfile}] if jobfile is not None else copy(self.prepared_jobs)
        )

        jobid_list = []

        if isinstance(dependency, list):
            dependency = ":".join(dependency)

        # TODO: Think about the issue when a job have too many dependencies and workaround.

        for i, jobinfo in enumerate(jobinfo_list):
            # open(job_dir.joinpath(f"tmp_{jobarray_uuid}_{i}.joblock"), "w").close() # Create a temp file with a unique uuid
            if "torque" in str(jobinfo["path"]).lower():
                cmd = (
                    ["qsub", f"-W depend=afterok:{dependency}", str(jobinfo["path"])]
                    if dependency
                    else ["qsub", str(jobinfo["path"])]
                )
                jobid = (
                    subprocess.run(cmd, stdout=subprocess.PIPE, check=False)
                    .stdout.decode("utf-8")
                    .rstrip("\n")
                )
                print(f"Sent command {' '.join(cmd)}")
                jobid_list.append(jobid)
            elif "slurm" in str(jobinfo["path"]).lower():
                dep = f"-d afterok:{dependency}" if dependency else ""
                jobid = (
                    subprocess.run(
                        ["sbatch", dep, jobinfo["path"]],
                        stdout=subprocess.PIPE,
                        check=False,
                    )
                    .stdout.decode("utf-8")
                    .rstrip("\n")
                )
                jobid_list.append(jobid)

            if jobinfo in self.prepared_jobs:
                self.__prepared_jobs.remove(jobinfo)
            jobinfo["id"] = jobid
            self.__ongoing_jobs.append(jobinfo)

        return jobid_list

    def update_job_status(self):
        """Iterates over the list of ongoing jobs and mark them as finished if the job file does not exist.
        Iterates over the list of finished jobs and remove them if the job outfile does not exist.
        """
        for jobinfo in self.__ongoing_jobs:
            if not jobinfo["path"].exists():
                self.__ongoing_jobs.remove(jobinfo)
                self.__finished_jobs.append(jobinfo)

    def update_job_access(self):
        """In case the output files are not accessible by anyone but the owner, running this once will update the permissions for anyone to read them."""
        for job_info in self.finished_jobs:
            try:
                if job_info["outfile"].exists():
                    chmod_if_needed(path=job_info["outfile"], mode=FPDEFAULT)
                if job_info["errfile"].exists():
                    chmod_if_needed(path=job_info["errfile"], mode=FPDEFAULT)
            except KeyError:
                print(f"No outfile or errfile associated with job {job_info['path']}.")

    def list_jobs(self):
        res = ""
        epoch = datetime.utcfromtimestamp(0)
        today = datetime.strftime(datetime.today(), "%d%m%y")
        if len(self.prepared_jobs) > 0:
            res += "==== PREPARED JOBS ====\n\n"
        for job_info in self.prepared_jobs:
            created_at = datetime.strptime(
                today + job_info["outfile"].stem[-11:-3],
                "%d%m%y%H-%M-%S",
            )
            res += (
                f"{job_info['job_name']} (created at {created_at}) : ready to start.\n"
            )

        if len(self.ongoing_jobs) > 0:
            res += "==== ONGOING JOBS ====\n\n"
        for job_info in self.ongoing_jobs:
            created_at = datetime.strptime(
                today + job_info["outfile"].stem[-11:-3],
                "%d%m%y%H-%M-%S",
            )
            delta = datetime.now() - created_at
            strftime = f"{'%H hours, ' if delta.seconds >= 3600 else ''}{'%M minutes and ' if delta.seconds >= 60 else ''}%S seconds"
            elapsed_time = datetime.strftime(epoch + delta, strftime)
            res += f"{job_info['job_name']} (created at {created_at}) : running for {elapsed_time}.\n"

        if len(self.finished_jobs) > 0:
            res += "==== FINISHED JOBS ====\n\n"
        for job_info in self.finished_jobs:
            created_at = datetime.strptime(
                today + job_info["outfile"].stem[-11:-3],
                "%d%m%y%H-%M-%S",
            )

            if not job_info["outfile"].exists():
                res += f"{job_info['job_name']} (created at {created_at}) : Output file still writing..."
            else:
                delta = (
                    datetime.fromtimestamp(
                        time.mktime(
                            time.localtime(job_info["outfile"].stat().st_ctime),
                        ),
                    )
                    - created_at
                )
                strftime = f"{'%H hours, ' if delta.seconds >= 3600 else ''}{'%M minutes and ' if delta.seconds >= 60 else ''}%S seconds"
                elapsed_time = datetime.strftime(epoch + delta, strftime)
                res += f"{job_info['job_name']} (created at {created_at}) : finished in {elapsed_time}.\n"

        if len(self.cancelled_jobs) > 0:
            res += "==== CANCELLED JOBS ====\n\n"
            for jobinfo in self.cancelled_jobs:
                res += f"{jobinfo['job_name']}"
        print(res)

    def read_output_file(
        self,
        *,
        job_name: str = None,
        outtype: Literal["out", "err"] = "out",
        job_file_name: str = None,
    ):
        """Read the content of a specific job output file, or the first in the finished list.

        Parameters
        ----------
            outtype: `{"out","err"}`, optional, keyword-only
                The type of the output file to read, whether standard (out) or error (err). The default is out.
            job_file_name: `str`, optional, keyword-only
                The path to the job_file to read, which can be retrieved easily from Job_builder.finished_jobs. If not provided, then the first element of the list will be read.

        """
        if outtype not in ["out", "err"]:
            raise ValueError(
                "The outtype must be either out for standard output file or err for error output file.",
            )

        if not job_file_name:
            job_id = 0
            if job_name:
                job_id = get_dict_index_in_list(
                    self.finished_jobs,
                    "job_name",
                    job_name.rstrip(),
                )
            elif len(self.finished_jobs) == 0:
                print(
                    f"There are no finished jobs in this context. Wait until the {len(self.ongoing_jobs)} ongoing jobs are done before reading the output. Otherwise, you can specify which file you wish to read.",
                )
                return

            job_file_name = (
                self.finished_jobs[job_id]["outfile"]
                if outtype == "out"
                else self.finished_jobs[job_id]["errfile"]
            )

        with open(job_file_name) as f:
            print("".join(f.readlines()))

    def delete_job(self, job_identifier: str):
        try:
            job_id = get_dict_index_in_list(
                self.ongoing_jobs,
                "job_name",
                job_identifier.rstrip(),
            )
        except ValueError:
            job_id = get_dict_index_in_list(
                self.ongoing_jobs,
                "id",
                job_identifier.rstrip(),
            )

        jobinfo = self.ongoing_jobs[job_id]
        if "Torque" in str(jobinfo["path"]):
            subprocess.run(["qdel", jobinfo["id"]], check=False)
        elif "Slurm" in str(jobinfo["path"]):
            subprocess.run(["scancel", jobinfo["id"]], check=False)
        self.__ongoing_jobs.remove(jobinfo)
        self.__cancelled_jobs.append(jobinfo)


def get_dict_index_in_list(item_list: list, key: str, value: any) -> int:
    for i, d in enumerate(item_list):
        if d[key] == value:
            return i

    raise ValueError(f"The value {value} appears nowhere in the {key} list.")
