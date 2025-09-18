# This file is part of ctrl_bps_htcondor.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This software is dual licensed under the GNU General Public License and also
# under a 3-clause BSD license. Recipients may choose which of these licenses
# to use; please see the files gpl-3.0.txt and/or bsd_license.txt,
# respectively.  If you choose the GPL option then the following text applies
# (but note that there is still no warranty even if you opt for BSD instead):
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Interface between generic workflow to HTCondor workflow system."""

__all__ = ["HTCondorService", "HTCondorWorkflow"]


import logging
import os
import re
from collections import defaultdict
from copy import deepcopy
from enum import IntEnum, auto
from pathlib import Path
from typing import Any, cast

import htcondor
from packaging import version

from lsst.ctrl.bps import (
    BaseWmsService,
    BaseWmsWorkflow,
    BpsConfig,
    GenericWorkflow,
    GenericWorkflowGroup,
    GenericWorkflowJob,
    GenericWorkflowNodeType,
    GenericWorkflowNoopJob,
    WmsJobReport,
    WmsRunReport,
    WmsSpecificInfo,
    WmsStates,
)
from lsst.ctrl.bps.bps_utils import chdir, create_count_summary
from lsst.daf.butler import Config
from lsst.utils.timer import time_this

from .htcondor_config import HTC_DEFAULTS_URI
from .lssthtc import (
    MISSING_ID,
    HTCDag,
    HTCJob,
    NodeStatus,
    WmsNodeType,
    _update_rescue_file,
    condor_history,
    condor_q,
    condor_search,
    condor_status,
    htc_backup_files,
    htc_check_dagman_output,
    htc_create_submit_from_cmd,
    htc_create_submit_from_dag,
    htc_create_submit_from_file,
    htc_escape,
    htc_submit_dag,
    htc_version,
    pegasus_name_to_label,
    read_dag_info,
    read_dag_log,
    read_dag_status,
    read_node_status,
    summarize_dag,
    write_dag_info,
)
from .provisioner import Provisioner


class WmsIdType(IntEnum):
    """Type of valid WMS ids."""

    UNKNOWN = auto()
    """The type of id cannot be determined.
    """

    LOCAL = auto()
    """The id is HTCondor job's ClusterId (with optional '.ProcId').
    """

    GLOBAL = auto()
    """Id is a HTCondor's global job id.
    """

    PATH = auto()
    """Id is a submission path.
    """


DEFAULT_HTC_EXEC_PATT = ".*worker.*"
"""Default pattern for searching execute machines in an HTCondor pool.
"""

_LOG = logging.getLogger(__name__)


class HTCondorService(BaseWmsService):
    """HTCondor version of WMS service."""

    @property
    def defaults(self):
        return Config(HTC_DEFAULTS_URI)

    @property
    def defaults_uri(self):
        return HTC_DEFAULTS_URI

    def prepare(self, config, generic_workflow, out_prefix=None):
        """Convert generic workflow to an HTCondor DAG ready for submission.

        Parameters
        ----------
        config : `lsst.ctrl.bps.BpsConfig`
            BPS configuration that includes necessary submit/runtime
            information.
        generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
            The generic workflow (e.g., has executable name and arguments).
        out_prefix : `str`
            The root directory into which all WMS-specific files are written.

        Returns
        -------
        workflow : `lsst.ctrl.bps.wms.htcondor.HTCondorWorkflow`
            HTCondor workflow ready to be run.
        """
        _LOG.debug("out_prefix = '%s'", out_prefix)
        with time_this(log=_LOG, level=logging.INFO, prefix=None, msg="Completed HTCondor workflow creation"):
            workflow = HTCondorWorkflow.from_generic_workflow(
                config,
                generic_workflow,
                out_prefix,
                f"{self.__class__.__module__}.{self.__class__.__name__}",
            )

            _, enable_provisioning = config.search("provisionResources")
            if enable_provisioning:
                provisioner = Provisioner(config)
                provisioner.configure()
                provisioner.prepare("provisioningJob.bash", prefix=out_prefix)
                provisioner.provision(workflow.dag)

        with time_this(
            log=_LOG, level=logging.INFO, prefix=None, msg="Completed writing out HTCondor workflow"
        ):
            workflow.write(out_prefix)
        return workflow

    def submit(self, workflow, **kwargs):
        """Submit a single HTCondor workflow.

        Parameters
        ----------
        workflow : `lsst.ctrl.bps.BaseWorkflow`
            A single HTCondor workflow to submit.  run_id is updated after
            successful submission to WMS.
        **kwargs : `~typing.Any`
            Keyword arguments for the options.
        """
        dag = workflow.dag
        ver = version.parse(htc_version())

        # For workflow portability, internal paths are all relative. Hence
        # the DAG needs to be submitted to HTCondor from inside the submit
        # directory.
        with chdir(workflow.submit_path):
            try:
                if ver >= version.parse("8.9.3"):
                    sub = htc_create_submit_from_dag(dag.graph["dag_filename"], dag.graph["submit_options"])
                else:
                    sub = htc_create_submit_from_cmd(dag.graph["dag_filename"], dag.graph["submit_options"])
            except Exception:
                _LOG.error(
                    "Problems creating HTCondor submit object from filename: %s", dag.graph["dag_filename"]
                )
                raise

            _LOG.info("Submitting from directory: %s", os.getcwd())
            schedd_dag_info = htc_submit_dag(sub)
            if schedd_dag_info:
                write_dag_info(f"{dag.name}.info.json", schedd_dag_info)

                _, dag_info = schedd_dag_info.popitem()
                _, dag_ad = dag_info.popitem()

                dag.run_id = f"{dag_ad['ClusterId']}.{dag_ad['ProcId']}"
                workflow.run_id = dag.run_id
            else:
                raise RuntimeError("Submission failed: unable to retrieve DAGMan job information")

    def restart(self, wms_workflow_id):
        """Restart a failed DAGMan workflow.

        Parameters
        ----------
        wms_workflow_id : `str`
            The directory with HTCondor files.

        Returns
        -------
        run_id : `str`
            HTCondor id of the restarted DAGMan job. If restart failed, it will
            be set to None.
        run_name : `str`
            Name of the restarted workflow. If restart failed, it will be set
            to None.
        message : `str`
            A message describing any issues encountered during the restart.
            If there were no issues, an empty string is returned.
        """
        wms_path, id_type = _wms_id_to_dir(wms_workflow_id)
        if wms_path is None:
            return (
                None,
                None,
                (
                    f"workflow with run id '{wms_workflow_id}' not found. "
                    "Hint: use run's submit directory as the id instead"
                ),
            )

        if id_type in {WmsIdType.GLOBAL, WmsIdType.LOCAL}:
            if not wms_path.is_dir():
                return None, None, f"submit directory '{wms_path}' for run id '{wms_workflow_id}' not found."

        _LOG.info("Restarting workflow from directory '%s'", wms_path)
        rescue_dags = list(wms_path.glob("*.dag.rescue*"))
        if not rescue_dags:
            return None, None, f"HTCondor rescue DAG(s) not found in '{wms_path}'"

        _LOG.info("Verifying that the workflow is not already in the job queue")
        schedd_dag_info = condor_q(constraint=f'regexp("dagman$", Cmd) && Iwd == "{wms_path}"')
        if schedd_dag_info:
            _, dag_info = schedd_dag_info.popitem()
            _, dag_ad = dag_info.popitem()
            id_ = dag_ad["GlobalJobId"]
            return None, None, f"Workflow already in the job queue (global job id: '{id_}')"

        _LOG.info("Checking execution status of the workflow")
        warn = False
        dag_ad = read_dag_status(str(wms_path))
        if dag_ad:
            nodes_total = dag_ad.get("NodesTotal", 0)
            if nodes_total != 0:
                nodes_done = dag_ad.get("NodesDone", 0)
                if nodes_total == nodes_done:
                    return None, None, "All jobs in the workflow finished successfully"
            else:
                warn = True
        else:
            warn = True
        if warn:
            _LOG.warning(
                "Cannot determine the execution status of the workflow, continuing with restart regardless"
            )

        _LOG.info("Backing up select HTCondor files from previous run attempt")
        rescue_file = htc_backup_files(wms_path, subdir="backups")
        if (wms_path / "subdags").exists():
            _update_rescue_file(rescue_file)

        # For workflow portability, internal paths are all relative. Hence
        # the DAG needs to be resubmitted to HTCondor from inside the submit
        # directory.
        _LOG.info("Adding workflow to the job queue")
        run_id, run_name, message = None, None, ""
        with chdir(wms_path):
            try:
                dag_path = next(Path.cwd().glob("*.dag.condor.sub"))
            except StopIteration:
                message = f"DAGMan submit description file not found in '{wms_path}'"
            else:
                sub = htc_create_submit_from_file(dag_path.name)
                schedd_dag_info = htc_submit_dag(sub)

                # Save select information about the DAGMan job to a file. Use
                # the run name (available in the ClassAd) as the filename.
                if schedd_dag_info:
                    dag_info = next(iter(schedd_dag_info.values()))
                    dag_ad = next(iter(dag_info.values()))
                    write_dag_info(f"{dag_ad['bps_run']}.info.json", schedd_dag_info)
                    run_id = f"{dag_ad['ClusterId']}.{dag_ad['ProcId']}"
                    run_name = dag_ad["bps_run"]
                else:
                    message = "DAGMan job information unavailable"

        return run_id, run_name, message

    def list_submitted_jobs(self, wms_id=None, user=None, require_bps=True, pass_thru=None, is_global=False):
        """Query WMS for list of submitted WMS workflows/jobs.

        This should be a quick lookup function to create list of jobs for
        other functions.

        Parameters
        ----------
        wms_id : `int` or `str`, optional
            Id or path that can be used by WMS service to look up job.
        user : `str`, optional
            User whose submitted jobs should be listed.
        require_bps : `bool`, optional
            Whether to require jobs returned in list to be bps-submitted jobs.
        pass_thru : `str`, optional
            Information to pass through to WMS.
        is_global : `bool`, optional
            If set, all job queues (and their histories) will be queried for
            job information. Defaults to False which means that only the local
            job queue will be queried.

        Returns
        -------
        job_ids : `list` [`~typing.Any`]
            Only job ids to be used by cancel and other functions.  Typically
            this means top-level jobs (i.e., not children jobs).
        """
        _LOG.debug(
            "list_submitted_jobs params: wms_id=%s, user=%s, require_bps=%s, pass_thru=%s, is_global=%s",
            wms_id,
            user,
            require_bps,
            pass_thru,
            is_global,
        )

        # Determine which Schedds will be queried for job information.
        coll = htcondor.Collector()

        schedd_ads = []
        if is_global:
            schedd_ads.extend(coll.locateAll(htcondor.DaemonTypes.Schedd))
        else:
            schedd_ads.append(coll.locate(htcondor.DaemonTypes.Schedd))

        # Construct appropriate constraint expression using provided arguments.
        constraint = "False"
        if wms_id is None:
            if user is not None:
                constraint = f'(Owner == "{user}")'
        else:
            schedd_ad, cluster_id, id_type = _wms_id_to_cluster(wms_id)
            if cluster_id is not None:
                constraint = f"(DAGManJobId == {cluster_id} || ClusterId == {cluster_id})"

                # If provided id is either a submission path or a global id,
                # make sure the right Schedd will be queried regardless of
                # 'is_global' value.
                if id_type in {WmsIdType.GLOBAL, WmsIdType.PATH}:
                    schedd_ads = [schedd_ad]
        if require_bps:
            constraint += ' && (bps_isjob == "True")'
        if pass_thru:
            if "-forcex" in pass_thru:
                pass_thru_2 = pass_thru.replace("-forcex", "")
                if pass_thru_2 and not pass_thru_2.isspace():
                    constraint += f" && ({pass_thru_2})"
            else:
                constraint += f" && ({pass_thru})"

        # Create a list of scheduler daemons which need to be queried.
        schedds = {ad["Name"]: htcondor.Schedd(ad) for ad in schedd_ads}

        _LOG.debug("constraint = %s, schedds = %s", constraint, ", ".join(schedds))
        results = condor_q(constraint=constraint, schedds=schedds)

        # Prune child jobs where DAG job is in queue (i.e., aren't orphans).
        job_ids = []
        for job_info in results.values():
            for job_id, job_ad in job_info.items():
                _LOG.debug("job_id=%s DAGManJobId=%s", job_id, job_ad.get("DAGManJobId", "None"))
                if "DAGManJobId" not in job_ad:
                    job_ids.append(job_ad.get("GlobalJobId", job_id))
                else:
                    _LOG.debug("Looking for %s", f"{job_ad['DAGManJobId']}.0")
                    _LOG.debug("\tin jobs.keys() = %s", job_info.keys())
                    if f"{job_ad['DAGManJobId']}.0" not in job_info:  # orphaned job
                        job_ids.append(job_ad.get("GlobalJobId", job_id))

        _LOG.debug("job_ids = %s", job_ids)
        return job_ids

    def get_status(
        self,
        wms_workflow_id: str,
        hist: float = 1,
        is_global: bool = False,
    ) -> tuple[WmsStates, str]:
        """Return status of run based upon given constraints.

        Parameters
        ----------
        wms_workflow_id : `str`
            Limit to specific run based on id (queue id or path).
        hist : `float`, optional
            Limit history search to this many days. Defaults to 1.
        is_global : `bool`, optional
            If set, all job queues (and their histories) will be queried for
            job information. Defaults to False which means that only the local
            job queue will be queried.

        Returns
        -------
        state : `lsst.ctrl.bps.WmsStates`
            Status of single run from given information.
        message : `str`
            Extra message for status command to print.  This could be pointers
            to documentation or to WMS specific commands.
        """
        _LOG.debug("get_status: id=%s, hist=%s, is_global=%s", wms_workflow_id, hist, is_global)

        id_type = _wms_id_type(wms_workflow_id)
        _LOG.debug("id_type = %s", id_type.name)

        if id_type == WmsIdType.LOCAL:
            schedulers = _locate_schedds(locate_all=is_global)
            _LOG.debug("schedulers = %s", schedulers)
            state, message = _get_status_from_id(wms_workflow_id, hist, schedds=schedulers)
        elif id_type == WmsIdType.GLOBAL:
            schedulers = _locate_schedds(locate_all=True)
            _LOG.debug("schedulers = %s", schedulers)
            state, message = _get_status_from_id(wms_workflow_id, hist, schedds=schedulers)
        elif id_type == WmsIdType.PATH:
            state, message = _get_status_from_path(wms_workflow_id)
        else:
            state, message = WmsStates.UNKNOWN, "Invalid job id"
        _LOG.debug("state: %s, %s", state, message)

        return state, message

    def report(
        self,
        wms_workflow_id=None,
        user=None,
        hist=0,
        pass_thru=None,
        is_global=False,
        return_exit_codes=False,
    ):
        """Return run information based upon given constraints.

        Parameters
        ----------
        wms_workflow_id : `str`, optional
            Limit to specific run based on id.
        user : `str`, optional
            Limit results to runs for this user.
        hist : `float`, optional
            Limit history search to this many days. Defaults to 0.
        pass_thru : `str`, optional
            Constraints to pass through to HTCondor.
        is_global : `bool`, optional
            If set, all job queues (and their histories) will be queried for
            job information. Defaults to False which means that only the local
            job queue will be queried.
        return_exit_codes : `bool`, optional
            If set, return exit codes related to jobs with a
            non-success status. Defaults to False, which means that only
            the summary state is returned.

            Only applicable in the context of a WMS with associated
            handlers to return exit codes from jobs.

        Returns
        -------
        runs : `list` [`lsst.ctrl.bps.WmsRunReport`]
            Information about runs from given job information.
        message : `str`
            Extra message for report command to print.  This could be pointers
            to documentation or to WMS specific commands.
        """
        if wms_workflow_id:
            id_type = _wms_id_type(wms_workflow_id)
            if id_type == WmsIdType.LOCAL:
                schedulers = _locate_schedds(locate_all=is_global)
                run_reports, message = _report_from_id(wms_workflow_id, hist, schedds=schedulers)
            elif id_type == WmsIdType.GLOBAL:
                schedulers = _locate_schedds(locate_all=True)
                run_reports, message = _report_from_id(wms_workflow_id, hist, schedds=schedulers)
            elif id_type == WmsIdType.PATH:
                run_reports, message = _report_from_path(wms_workflow_id)
            else:
                run_reports, message = {}, "Invalid job id"
        else:
            schedulers = _locate_schedds(locate_all=is_global)
            run_reports, message = _summary_report(user, hist, pass_thru, schedds=schedulers)
        _LOG.debug("report: %s, %s", run_reports, message)

        return list(run_reports.values()), message

    def cancel(self, wms_id, pass_thru=None):
        """Cancel submitted workflows/jobs.

        Parameters
        ----------
        wms_id : `str`
            Id or path of job that should be canceled.
        pass_thru : `str`, optional
            Information to pass through to WMS.

        Returns
        -------
        deleted : `bool`
            Whether successful deletion or not.  Currently, if any doubt or any
            individual jobs not deleted, return False.
        message : `str`
            Any message from WMS (e.g., error details).
        """
        _LOG.debug("Canceling wms_id = %s", wms_id)

        schedd_ad, cluster_id, _ = _wms_id_to_cluster(wms_id)

        if cluster_id is None:
            deleted = False
            message = "invalid id"
        else:
            _LOG.debug(
                "Canceling job managed by schedd_name = %s with cluster_id = %s",
                cluster_id,
                schedd_ad["Name"],
            )
            schedd = htcondor.Schedd(schedd_ad)

            constraint = f"ClusterId == {cluster_id}"
            if pass_thru is not None and "-forcex" in pass_thru:
                pass_thru_2 = pass_thru.replace("-forcex", "")
                if pass_thru_2 and not pass_thru_2.isspace():
                    constraint += f"&& ({pass_thru_2})"
                _LOG.debug("JobAction.RemoveX constraint = %s", constraint)
                results = schedd.act(htcondor.JobAction.RemoveX, constraint)
            else:
                if pass_thru:
                    constraint += f"&& ({pass_thru})"
                _LOG.debug("JobAction.Remove constraint = %s", constraint)
                results = schedd.act(htcondor.JobAction.Remove, constraint)
            _LOG.debug("Remove results: %s", results)

            if results["TotalSuccess"] > 0 and results["TotalError"] == 0:
                deleted = True
                message = ""
            else:
                deleted = False
                if results["TotalSuccess"] == 0 and results["TotalError"] == 0:
                    message = "no such bps job in batch queue"
                else:
                    message = f"unknown problems deleting: {results}"

        _LOG.debug("deleted: %s; message = %s", deleted, message)
        return deleted, message

    def ping(self, pass_thru):
        """Check whether WMS services are up, reachable, and can authenticate
        if authentication is required.

        The services to be checked are those needed for submit, report, cancel,
        restart, but ping cannot guarantee whether jobs would actually run
        successfully.

        Parameters
        ----------
        pass_thru : `str`, optional
            Information to pass through to WMS.

        Returns
        -------
        status : `int`
            0 for success, non-zero for failure.
        message : `str`
            Any message from WMS (e.g., error details).
        """
        coll = htcondor.Collector()
        secman = htcondor.SecMan()
        status = 0
        message = ""
        _LOG.info("Not verifying that compute resources exist.")
        try:
            for daemon_type in [htcondor.DaemonTypes.Schedd, htcondor.DaemonTypes.Collector]:
                _ = secman.ping(coll.locate(daemon_type))
        except htcondor.HTCondorLocateError:
            status = 1
            message = f"Could not locate {daemon_type} service."
        except htcondor.HTCondorIOError:
            status = 1
            message = f"Permission problem with {daemon_type} service."
        return status, message


class HTCondorWorkflow(BaseWmsWorkflow):
    """Single HTCondor workflow.

    Parameters
    ----------
    name : `str`
        Unique name for Workflow used when naming files.
    config : `lsst.ctrl.bps.BpsConfig`
        BPS configuration that includes necessary submit/runtime information.
    """

    def __init__(self, name, config=None):
        super().__init__(name, config)
        self.dag = None

    @classmethod
    def from_generic_workflow(cls, config, generic_workflow, out_prefix, service_class):
        # Docstring inherited
        htc_workflow = cls(generic_workflow.name, config)
        htc_workflow.dag = _generic_workflow_to_htcondor_dag(config, generic_workflow, out_prefix)

        _LOG.debug("htcondor dag attribs %s", generic_workflow.run_attrs)
        # Add extra attributes to top most DAG.
        htc_workflow.dag.add_attribs(
            {
                "bps_wms_service": service_class,
                "bps_wms_workflow": f"{cls.__module__}.{cls.__name__}",
            }
        )

        return htc_workflow

    def write(self, out_prefix):
        """Output HTCondor DAGMan files needed for workflow submission.

        Parameters
        ----------
        out_prefix : `str`
            Directory prefix for HTCondor files.
        """
        self.submit_path = out_prefix
        os.makedirs(out_prefix, exist_ok=True)

        # Write down the workflow in HTCondor format.
        self.dag.write(out_prefix, job_subdir="jobs/{self.label}")


def _create_job(subdir_template, cached_values, generic_workflow, gwjob, out_prefix):
    """Convert GenericWorkflow job nodes to DAG jobs.

    Parameters
    ----------
    subdir_template : `str`
        Template for making subdirs.
    cached_values : `dict`
        Site and label specific values.
    generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
        Generic workflow that is being converted.
    gwjob : `lsst.ctrl.bps.GenericWorkflowJob`
        The generic job to convert to a HTCondor job.
    out_prefix : `str`
        Directory prefix for HTCondor files.

    Returns
    -------
    htc_job : `lsst.ctrl.bps.wms.htcondor.HTCJob`
        The HTCondor job equivalent to the given generic job.
    """
    htc_job = HTCJob(gwjob.name, label=gwjob.label)

    curvals = defaultdict(str)
    curvals["label"] = gwjob.label
    if gwjob.tags:
        curvals.update(gwjob.tags)

    subdir = Path("jobs") / subdir_template.format_map(curvals)
    htc_job.subdir = subdir
    htc_job.subfile = f"{gwjob.name}.sub"
    htc_job.add_dag_cmds({"dir": subdir})

    htc_job_cmds = {
        "universe": "vanilla",
        "should_transfer_files": "YES",
        "when_to_transfer_output": "ON_EXIT_OR_EVICT",
        "transfer_output_files": '""',  # Set to empty string to disable
        "transfer_executable": "False",
        "getenv": "True",
        # Exceeding memory sometimes triggering SIGBUS or SIGSEGV error. Tell
        # htcondor to put on hold any jobs which exited by a signal.
        "on_exit_hold": "ExitBySignal == true",
        "on_exit_hold_reason": (
            'strcat("Job raised a signal ", string(ExitSignal), ". ", '
            '"Handling signal as if job has gone over memory limit.")'
        ),
        "on_exit_hold_subcode": "34",
    }

    htc_job_cmds.update(_translate_job_cmds(cached_values, generic_workflow, gwjob))

    # Combine stdout and stderr to reduce the number of files.
    for key in ("output", "error"):
        if cached_values["overwriteJobFiles"]:
            htc_job_cmds[key] = f"{gwjob.name}.$(Cluster).out"
        else:
            htc_job_cmds[key] = f"{gwjob.name}.$(Cluster).$$([NumJobStarts ?: 0]).out"
        _LOG.debug("HTCondor %s = %s", key, htc_job_cmds[key])

    key = "log"
    htc_job_cmds[key] = f"{gwjob.name}.$(Cluster).{key}"
    _LOG.debug("HTCondor %s = %s", key, htc_job_cmds[key])

    htc_job_cmds.update(
        _handle_job_inputs(generic_workflow, gwjob.name, cached_values["bpsUseShared"], out_prefix)
    )

    htc_job_cmds.update(
        _handle_job_outputs(generic_workflow, gwjob.name, cached_values["bpsUseShared"], out_prefix)
    )

    # Add the job cmds dict to the job object.
    htc_job.add_job_cmds(htc_job_cmds)

    htc_job.add_dag_cmds(_translate_dag_cmds(gwjob))

    # Add job attributes to job.
    _LOG.debug("gwjob.attrs = %s", gwjob.attrs)
    htc_job.add_job_attrs(gwjob.attrs)
    htc_job.add_job_attrs(cached_values["attrs"])
    htc_job.add_job_attrs({"bps_job_quanta": create_count_summary(gwjob.quanta_counts)})
    htc_job.add_job_attrs({"bps_job_name": gwjob.name, "bps_job_label": gwjob.label})

    return htc_job


def _translate_job_cmds(cached_vals, generic_workflow, gwjob):
    """Translate the job data that are one to one mapping

    Parameters
    ----------
    cached_vals : `dict` [`str`, `~typing.Any`]
        Config values common to jobs with same site or label.
    generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
        Generic workflow that contains job to being converted.
    gwjob : `lsst.ctrl.bps.GenericWorkflowJob`
        Generic workflow job to be converted.

    Returns
    -------
    htc_job_commands : `dict` [`str`, `~typing.Any`]
        Contains commands which can appear in the HTCondor submit description
        file.
    """
    # Values in the job script that just are name mappings.
    job_translation = {
        "mail_to": "notify_user",
        "when_to_mail": "notification",
        "request_cpus": "request_cpus",
        "priority": "priority",
        "category": "category",
        "accounting_group": "accounting_group",
        "accounting_user": "accounting_group_user",
    }

    jobcmds = {}
    for gwkey, htckey in job_translation.items():
        jobcmds[htckey] = getattr(gwjob, gwkey, None)

    # If accounting info was not set explicitly, use site settings if any.
    if not gwjob.accounting_group:
        jobcmds["accounting_group"] = cached_vals.get("accountingGroup")
    if not gwjob.accounting_user:
        jobcmds["accounting_group_user"] = cached_vals.get("accountingUser")

    # job commands that need modification
    if gwjob.retry_unless_exit:
        if isinstance(gwjob.retry_unless_exit, int):
            jobcmds["retry_until"] = f"{gwjob.retry_unless_exit}"
        elif isinstance(gwjob.retry_unless_exit, list):
            jobcmds["retry_until"] = (
                f"member(ExitCode, {{{','.join([str(x) for x in gwjob.retry_unless_exit])}}})"
            )
        else:
            raise ValueError("retryUnlessExit must be an integer or a list of integers.")

    if gwjob.request_disk:
        jobcmds["request_disk"] = f"{gwjob.request_disk}MB"

    if gwjob.request_memory:
        jobcmds["request_memory"] = f"{gwjob.request_memory}"

    memory_max = 0
    if gwjob.memory_multiplier:
        # Do not use try-except! At the moment, BpsConfig returns an empty
        # string if it does not contain the key.
        memory_limit = cached_vals["memoryLimit"]
        if not memory_limit:
            raise RuntimeError(
                "Memory autoscaling enabled, but automatic detection of the memory limit "
                "failed; setting it explicitly with 'memoryLimit' or changing worker node "
                "search pattern 'executeMachinesPattern' might help."
            )

        # Set maximal amount of memory job can ask for.
        #
        # The check below assumes that 'memory_limit' was set to a value which
        # realistically reflects actual physical limitations of a given compute
        # resource.
        memory_max = memory_limit
        if gwjob.request_memory_max and gwjob.request_memory_max < memory_limit:
            memory_max = gwjob.request_memory_max

        # Make job ask for more memory each time it failed due to insufficient
        # memory requirements.
        jobcmds["request_memory"] = _create_request_memory_expr(
            gwjob.request_memory, gwjob.memory_multiplier, memory_max
        )

    user_release_expr = cached_vals.get("releaseExpr", "")
    if gwjob.number_of_retries is not None and gwjob.number_of_retries >= 0:
        jobcmds["max_retries"] = gwjob.number_of_retries

        # No point in adding periodic_release if 0 retries
        if gwjob.number_of_retries > 0:
            periodic_release = _create_periodic_release_expr(
                gwjob.request_memory, gwjob.memory_multiplier, memory_max, user_release_expr
            )
            if periodic_release:
                jobcmds["periodic_release"] = periodic_release

        jobcmds["periodic_remove"] = _create_periodic_remove_expr(
            gwjob.request_memory, gwjob.memory_multiplier, memory_max
        )

    # Assume concurrency_limit implemented using HTCondor concurrency limits.
    # May need to move to special site-specific implementation if sites use
    # other mechanisms.
    if gwjob.concurrency_limit:
        jobcmds["concurrency_limit"] = gwjob.concurrency_limit

    # Handle command line
    if gwjob.executable.transfer_executable:
        jobcmds["transfer_executable"] = "True"
        jobcmds["executable"] = gwjob.executable.src_uri
    else:
        jobcmds["executable"] = _fix_env_var_syntax(gwjob.executable.src_uri)

    if gwjob.arguments:
        arguments = gwjob.arguments
        arguments = _replace_cmd_vars(arguments, gwjob)
        arguments = _replace_file_vars(cached_vals["bpsUseShared"], arguments, generic_workflow, gwjob)
        arguments = _fix_env_var_syntax(arguments)
        jobcmds["arguments"] = arguments

    if gwjob.environment:
        env_str = ""
        for name, value in gwjob.environment.items():
            if isinstance(value, str):
                value2 = _replace_cmd_vars(value, gwjob)
                value2 = _fix_env_var_syntax(value2)
                value2 = htc_escape(value2)
                env_str += f"{name}='{value2}' "  # Add single quotes to allow internal spaces
            else:
                env_str += f"{name}={value} "

        # Process above added one trailing space
        jobcmds["environment"] = env_str.rstrip()

    # Add extra "pass-thru" job commands
    if gwjob.profile:
        for key, val in gwjob.profile.items():
            jobcmds[key] = htc_escape(val)
    for key, val in cached_vals["profile"].items():
        jobcmds[key] = htc_escape(val)

    return jobcmds


def _translate_dag_cmds(gwjob):
    """Translate job values into DAGMan commands.

    Parameters
    ----------
    gwjob : `lsst.ctrl.bps.GenericWorkflowJob`
        Job containing values to be translated.

    Returns
    -------
    dagcmds : `dict` [`str`, `~typing.Any`]
        DAGMan commands for the job.
    """
    # Values in the dag script that just are name mappings.
    dag_translation = {"abort_on_value": "abort_dag_on", "abort_return_value": "abort_exit"}

    dagcmds = {}
    for gwkey, htckey in dag_translation.items():
        dagcmds[htckey] = getattr(gwjob, gwkey, None)

    # Still to be coded: vars "pre_cmdline", "post_cmdline"
    return dagcmds


def _fix_env_var_syntax(oldstr):
    """Change ENV place holders to HTCondor Env var syntax.

    Parameters
    ----------
    oldstr : `str`
        String in which environment variable syntax is to be fixed.

    Returns
    -------
    newstr : `str`
        Given string with environment variable syntax fixed.
    """
    newstr = oldstr
    for key in re.findall(r"<ENV:([^>]+)>", oldstr):
        newstr = newstr.replace(rf"<ENV:{key}>", f"$ENV({key})")
    return newstr


def _replace_file_vars(use_shared, arguments, workflow, gwjob):
    """Replace file placeholders in command line arguments with correct
    physical file names.

    Parameters
    ----------
    use_shared : `bool`
        Whether HTCondor can assume shared filesystem.
    arguments : `str`
        Arguments string in which to replace file placeholders.
    workflow : `lsst.ctrl.bps.GenericWorkflow`
        Generic workflow that contains file information.
    gwjob : `lsst.ctrl.bps.GenericWorkflowJob`
        The job corresponding to the arguments.

    Returns
    -------
    arguments : `str`
        Given arguments string with file placeholders replaced.
    """
    # Replace input file placeholders with paths.
    for gwfile in workflow.get_job_inputs(gwjob.name, data=True, transfer_only=False):
        if not gwfile.wms_transfer:
            # Must assume full URI if in command line and told WMS is not
            # responsible for transferring file.
            uri = gwfile.src_uri
        elif use_shared:
            if gwfile.job_shared:
                # Have shared filesystems and jobs can share file.
                uri = gwfile.src_uri
            else:
                uri = os.path.basename(gwfile.src_uri)
        else:  # Using push transfer
            uri = os.path.basename(gwfile.src_uri)
        arguments = arguments.replace(f"<FILE:{gwfile.name}>", uri)

    # Replace output file placeholders with paths.
    for gwfile in workflow.get_job_outputs(gwjob.name, data=True, transfer_only=False):
        if not gwfile.wms_transfer:
            # Must assume full URI if in command line and told WMS is not
            # responsible for transferring file.
            uri = gwfile.src_uri
        elif use_shared:
            if gwfile.job_shared:
                # Have shared filesystems and jobs can share file.
                uri = gwfile.src_uri
            else:
                uri = os.path.basename(gwfile.src_uri)
        else:  # Using push transfer
            uri = os.path.basename(gwfile.src_uri)
        arguments = arguments.replace(f"<FILE:{gwfile.name}>", uri)
    return arguments


def _replace_cmd_vars(arguments, gwjob):
    """Replace format-style placeholders in arguments.

    Parameters
    ----------
    arguments : `str`
        Arguments string in which to replace placeholders.
    gwjob : `lsst.ctrl.bps.GenericWorkflowJob`
        Job containing values to be used to replace placeholders
        (in particular gwjob.cmdvals).

    Returns
    -------
    arguments : `str`
        Given arguments string with placeholders replaced.
    """
    replacements = gwjob.cmdvals if gwjob.cmdvals is not None else {}
    try:
        arguments = arguments.format(**replacements)
    except (KeyError, TypeError) as exc:  # TypeError in case None instead of {}
        _LOG.error("Could not replace command variables: replacement for %s not provided", str(exc))
        _LOG.debug("arguments: %s\ncmdvals: %s", arguments, replacements)
        raise
    return arguments


def _handle_job_inputs(
    generic_workflow: GenericWorkflow, job_name: str, use_shared: bool, out_prefix: str
) -> dict[str, str]:
    """Add job input files from generic workflow to job.

    Parameters
    ----------
    generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
        The generic workflow (e.g., has executable name and arguments).
    job_name : `str`
        Unique name for the job.
    use_shared : `bool`
        Whether job has access to files via shared filesystem.
    out_prefix : `str`
        The root directory into which all WMS-specific files are written.

    Returns
    -------
    htc_commands : `dict` [`str`, `str`]
        HTCondor commands for the job submission script.
    """
    inputs = []
    for gwf_file in generic_workflow.get_job_inputs(job_name, data=True, transfer_only=True):
        _LOG.debug("src_uri=%s", gwf_file.src_uri)

        uri = Path(gwf_file.src_uri)

        # Note if use_shared and job_shared, don't need to transfer file.

        if not use_shared:  # Copy file using push to job
            inputs.append(str(uri))
        elif not gwf_file.job_shared:  # Jobs require own copy
            # if using shared filesystem, but still need copy in job. Use
            # HTCondor's curl plugin for a local copy.
            if uri.is_dir():
                raise RuntimeError(
                    f"HTCondor plugin cannot transfer directories locally within job {gwf_file.src_uri}"
                )
            inputs.append(f"file://{uri}")

    htc_commands = {}
    if inputs:
        htc_commands["transfer_input_files"] = ",".join(inputs)
        _LOG.debug("transfer_input_files=%s", htc_commands["transfer_input_files"])
    return htc_commands


def _handle_job_outputs(
    generic_workflow: GenericWorkflow, job_name: str, use_shared: bool, out_prefix: str
) -> dict[str, str]:
    """Add job output files from generic workflow to the job if any.

    Parameters
    ----------
    generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
        The generic workflow (e.g., has executable name and arguments).
    job_name : `str`
        Unique name for the job.
    use_shared : `bool`
        Whether job has access to files via shared filesystem.
    out_prefix : `str`
        The root directory into which all WMS-specific files are written.

    Returns
    -------
    htc_commands : `dict` [`str`, `str`]
        HTCondor commands for the job submission script.
    """
    outputs = []
    output_remaps = []
    for gwf_file in generic_workflow.get_job_outputs(job_name, data=True, transfer_only=True):
        _LOG.debug("src_uri=%s", gwf_file.src_uri)

        uri = Path(gwf_file.src_uri)
        if not use_shared:
            outputs.append(uri.name)
            output_remaps.append(f"{uri.name}={str(uri)}")

    # Set to an empty string to disable and only update if there are output
    # files to transfer. Otherwise, HTCondor will transfer back all files in
    # the job’s temporary working directory that have been modified or created
    # by the job.
    htc_commands = {"transfer_output_files": '""'}
    if outputs:
        htc_commands["transfer_output_files"] = ",".join(outputs)
        _LOG.debug("transfer_output_files=%s", htc_commands["transfer_output_files"])

        htc_commands["transfer_output_remaps"] = f'"{";".join(output_remaps)}"'
        _LOG.debug("transfer_output_remaps=%s", htc_commands["transfer_output_remaps"])
    return htc_commands


def _get_status_from_id(
    wms_workflow_id: str, hist: float, schedds: dict[str, htcondor.Schedd]
) -> tuple[WmsStates, str]:
    """Gather run information using workflow id.

    Parameters
    ----------
    wms_workflow_id : `str`
        Limit to specific run based on id.
    hist : `float`
        Limit history search to this many days.
    schedds : `dict` [ `str`, `htcondor.Schedd` ]
        HTCondor schedulers which to query for job information. If empty
        dictionary, all queries will be run against the local scheduler only.

    Returns
    -------
    state : `lsst.ctrl.bps.WmsStates`
        Status for the corresponding run.
    message : `str`
        Message with extra error information.
    """
    _LOG.debug("_get_status_from_id: id=%s, hist=%s, schedds=%s", wms_workflow_id, hist, schedds)

    message = ""

    # Collect information about the job by querying HTCondor schedd and
    # HTCondor history.
    schedd_dag_info = _get_info_from_schedd(wms_workflow_id, hist, schedds)
    if len(schedd_dag_info) == 1:
        schedd_name = next(iter(schedd_dag_info))
        dag_id = next(iter(schedd_dag_info[schedd_name]))
        dag_ad = schedd_dag_info[schedd_name][dag_id]
        state = _htc_status_to_wms_state(dag_ad)
    else:
        state = WmsStates.UNKNOWN
        message = f"DAGMan job {wms_workflow_id} not found in queue or history.  Check id or try path."
    return state, message


def _get_status_from_path(wms_path: str | os.PathLike) -> tuple[WmsStates, str]:
    """Gather run status from a given run directory.

    Parameters
    ----------
    wms_path : `str` | `os.PathLike`
        The directory containing the submit side files (e.g., HTCondor files).

    Returns
    -------
    state : `lsst.ctrl.bps.WmsStates`
        Status for the run.
    message : `str`
        Message to be printed.
    """
    wms_path = Path(wms_path).resolve()
    message = ""
    try:
        wms_workflow_id, dag_ad = read_dag_log(wms_path)
    except FileNotFoundError:
        wms_workflow_id = MISSING_ID
        message = f"DAGMan log not found in {wms_path}.  Check path."

    if wms_workflow_id == MISSING_ID:
        state = WmsStates.UNKNOWN
    else:
        state = _htc_status_to_wms_state(dag_ad[wms_workflow_id])

    return state, message


def _report_from_path(wms_path):
    """Gather run information from a given run directory.

    Parameters
    ----------
    wms_path : `str`
        The directory containing the submit side files (e.g., HTCondor files).

    Returns
    -------
    run_reports : `dict` [`str`, `lsst.ctrl.bps.WmsRunReport`]
        Run information for the detailed report.  The key is the HTCondor id
        and the value is a collection of report information for that run.
    message : `str`
        Message to be printed with the summary report.
    """
    wms_workflow_id, jobs, message = _get_info_from_path(wms_path)
    if wms_workflow_id == MISSING_ID:
        run_reports = {}
    else:
        run_reports = _create_detailed_report_from_jobs(wms_workflow_id, jobs)
    return run_reports, message


def _report_from_id(wms_workflow_id, hist, schedds=None):
    """Gather run information using workflow id.

    Parameters
    ----------
    wms_workflow_id : `str`
        Limit to specific run based on id.
    hist : `float`
        Limit history search to this many days.
    schedds : `dict` [ `str`, `htcondor.Schedd` ], optional
        HTCondor schedulers which to query for job information. If None
        (default), all queries will be run against the local scheduler only.

    Returns
    -------
    run_reports : `dict` [`str`, `lsst.ctrl.bps.WmsRunReport`]
        Run information for the detailed report.  The key is the HTCondor id
        and the value is a collection of report information for that run.
    message : `str`
        Message to be printed with the summary report.
    """
    messages = []

    # Collect information about the job by querying HTCondor schedd and
    # HTCondor history.
    schedd_dag_info = _get_info_from_schedd(wms_workflow_id, hist, schedds)
    if len(schedd_dag_info) == 1:
        # Extract the DAG info without altering the results of the query.
        schedd_name = next(iter(schedd_dag_info))
        dag_id = next(iter(schedd_dag_info[schedd_name]))
        dag_ad = schedd_dag_info[schedd_name][dag_id]

        # If the provided workflow id does not correspond to the one extracted
        # from the DAGMan log file in the submit directory, rerun the query
        # with the id found in the file.
        #
        # This is to cover the situation in which the user provided the old job
        # id of a restarted run.
        try:
            path_dag_id, _ = read_dag_log(dag_ad["Iwd"])
        except FileNotFoundError as exc:
            # At the moment missing DAGMan log is pretty much a fatal error.
            # So empty the DAG info to finish early (see the if statement
            # below).
            schedd_dag_info.clear()
            messages.append(f"Cannot create the report for '{dag_id}': {exc}")
        else:
            if path_dag_id != dag_id:
                schedd_dag_info = _get_info_from_schedd(path_dag_id, hist, schedds)
                messages.append(
                    f"WARNING: Found newer workflow executions in same submit directory as id '{dag_id}'. "
                    "This normally occurs when a run is restarted. The report shown is for the most "
                    f"recent status with run id '{path_dag_id}'"
                )

    if len(schedd_dag_info) == 0:
        run_reports = {}
    elif len(schedd_dag_info) == 1:
        _, dag_info = schedd_dag_info.popitem()
        dag_id, dag_ad = dag_info.popitem()

        # Create a mapping between jobs and their classads. The keys will
        # be of format 'ClusterId.ProcId'.
        job_info = {dag_id: dag_ad}

        # Find jobs (nodes) belonging to that DAGMan job.
        job_constraint = f"DAGManJobId == {int(float(dag_id))}"
        schedd_job_info = condor_search(constraint=job_constraint, hist=hist, schedds=schedds)
        if schedd_job_info:
            _, node_info = schedd_job_info.popitem()
            job_info.update(node_info)

        # Collect additional pieces of information about jobs using HTCondor
        # files in the submission directory.
        _, path_jobs, message = _get_info_from_path(dag_ad["Iwd"])
        _update_jobs(job_info, path_jobs)
        if message:
            messages.append(message)
        run_reports = _create_detailed_report_from_jobs(dag_id, job_info)
    else:
        ids = [ad["GlobalJobId"] for dag_info in schedd_dag_info.values() for ad in dag_info.values()]
        message = (
            f"More than one job matches id '{wms_workflow_id}', "
            f"their global ids are: {', '.join(ids)}. Rerun with one of the global ids"
        )
        messages.append(message)
        run_reports = {}

    message = "\n".join(messages)
    return run_reports, message


def _get_info_from_schedd(
    wms_workflow_id: str, hist: float, schedds: dict[str, htcondor.Schedd]
) -> dict[str, dict[str, dict[str, Any]]]:
    """Gather run information from HTCondor.

    Parameters
    ----------
    wms_workflow_id : `str`
        Limit to specific run based on id.
    hist : `float`
        Limit history search to this many days.
    schedds : `dict` [ `str`, `htcondor.Schedd` ]
        HTCondor schedulers which to query for job information. If empty
        dictionary, all queries will be run against the local scheduler only.

    Returns
    -------
    schedd_dag_info : `dict` [`str`, `dict` [`str`, `dict` [`str` Any]]]
        Information about jobs satisfying the search criteria where for each
        Scheduler, local HTCondor job ids are mapped to their respective
        classads.
    """
    _LOG.debug("_get_info_from_schedd: id=%s, hist=%s, schedds=%s", wms_workflow_id, hist, schedds)

    dag_constraint = 'regexp("dagman$", Cmd)'
    try:
        cluster_id = int(float(wms_workflow_id))
    except ValueError:
        dag_constraint += f' && GlobalJobId == "{wms_workflow_id}"'
    else:
        dag_constraint += f" && ClusterId == {cluster_id}"

    # With the current implementation of the condor_* functions the query
    # will always return only one match per Scheduler.
    #
    # Even in the highly unlikely situation where HTCondor history (which
    # condor_search queries too) is long enough to have jobs from before
    # the cluster ids were rolled over (and as a result there is more then
    # one job with the same cluster id) they will not show up in
    # the results.
    schedd_dag_info = condor_search(constraint=dag_constraint, hist=hist, schedds=schedds)
    return schedd_dag_info


def _get_info_from_path(wms_path: str | os.PathLike) -> tuple[str, dict[str, dict[str, Any]], str]:
    """Gather run information from a given run directory.

    Parameters
    ----------
    wms_path : `str` or `os.PathLike`
        Directory containing HTCondor files.

    Returns
    -------
    wms_workflow_id : `str`
        The run id which is a DAGman job id.
    jobs : `dict` [`str`, `dict` [`str`, `~typing.Any`]]
        Information about jobs read from files in the given directory.
        The key is the HTCondor id and the value is a dictionary of HTCondor
        keys and values.
    message : `str`
        Message to be printed with the summary report.
    """
    # Ensure path is absolute, in particular for folks helping
    # debug failures that need to dig around submit files.
    wms_path = Path(wms_path).resolve()

    messages = []
    try:
        wms_workflow_id, jobs = read_dag_log(wms_path)
        _LOG.debug("_get_info_from_path: from dag log %s = %s", wms_workflow_id, jobs)
        _update_jobs(jobs, read_node_status(wms_path))
        _LOG.debug("_get_info_from_path: after node status %s = %s", wms_workflow_id, jobs)

        # Add more info for DAGman job
        job = jobs[wms_workflow_id]
        job.update(read_dag_status(wms_path))

        job["total_jobs"], job["state_counts"] = _get_state_counts_from_jobs(wms_workflow_id, jobs)
        if "bps_run" not in job:
            _add_run_info(wms_path, job)

        message = htc_check_dagman_output(wms_path)
        if message:
            messages.append(message)
        _LOG.debug(
            "_get_info: id = %s, total_jobs = %s", wms_workflow_id, jobs[wms_workflow_id]["total_jobs"]
        )

        # Add extra pieces of information which cannot be found in HTCondor
        # generated files like 'GlobalJobId'.
        #
        # Do not treat absence of this file as a serious error. Neither runs
        # submitted with earlier versions of the plugin nor the runs submitted
        # with Pegasus plugin will have it at the moment. However, once enough
        # time passes and Pegasus plugin will have its own report() method
        # (instead of sneakily using HTCondor's one), the lack of that file
        # should be treated as seriously as lack of any other file.
        try:
            job_info = read_dag_info(wms_path)
        except FileNotFoundError as exc:
            message = f"Warn: Some information may not be available: {exc}"
            messages.append(message)
        else:
            schedd_name = next(iter(job_info))
            job_ad = next(iter(job_info[schedd_name].values()))
            job.update(job_ad)
    except FileNotFoundError as err:
        message = f"Could not find HTCondor files in '{wms_path}' ({err})"
        _LOG.debug(message)
        messages.append(message)
        message = htc_check_dagman_output(wms_path)
        if message:
            messages.append(message)
        wms_workflow_id = MISSING_ID
        jobs = {}

    message = "\n".join([msg for msg in messages if msg])
    _LOG.debug("wms_workflow_id = %s, jobs = %s", wms_workflow_id, jobs.keys())
    _LOG.debug("message = %s", message)
    return wms_workflow_id, jobs, message


def _create_detailed_report_from_jobs(
    wms_workflow_id: str, jobs: dict[str, dict[str, Any]]
) -> dict[str, WmsRunReport]:
    """Gather run information to be used in generating summary reports.

    Parameters
    ----------
    wms_workflow_id : `str`
        The run id to create the report for.
    jobs : `dict` [`str`, `dict` [`str`, Any]]
        Mapping HTCondor job id to job information.

    Returns
    -------
    run_reports : `dict` [`str`, `lsst.ctrl.bps.WmsRunReport`]
        Run information for the detailed report.  The key is the given HTCondor
        id and the value is a collection of report information for that run.
    """
    _LOG.debug("_create_detailed_report: id = %s, job = %s", wms_workflow_id, jobs[wms_workflow_id])

    dag_ad = jobs[wms_workflow_id]

    report = WmsRunReport(
        wms_id=f"{dag_ad['ClusterId']}.{dag_ad['ProcId']}",
        global_wms_id=dag_ad.get("GlobalJobId", "MISS"),
        path=dag_ad["Iwd"],
        label=dag_ad.get("bps_job_label", "MISS"),
        run=dag_ad.get("bps_run", "MISS"),
        project=dag_ad.get("bps_project", "MISS"),
        campaign=dag_ad.get("bps_campaign", "MISS"),
        payload=dag_ad.get("bps_payload", "MISS"),
        operator=_get_owner(dag_ad),
        run_summary=_get_run_summary(dag_ad),
        state=_htc_status_to_wms_state(dag_ad),
        total_number_jobs=0,
        jobs=[],
        job_state_counts=dict.fromkeys(WmsStates, 0),
        exit_code_summary={},
    )

    payload_jobs = {}  # keep track for later processing
    specific_info = WmsSpecificInfo()
    for job_id, job_ad in jobs.items():
        if job_ad.get("wms_node_type", WmsNodeType.UNKNOWN) in [WmsNodeType.PAYLOAD, WmsNodeType.FINAL]:
            try:
                name = job_ad.get("DAGNodeName", job_id)
                wms_state = _htc_status_to_wms_state(job_ad)
                job_report = WmsJobReport(
                    wms_id=job_id,
                    name=name,
                    label=job_ad.get("bps_job_label", pegasus_name_to_label(name)),
                    state=wms_state,
                )
                if job_report.label == "init":
                    job_report.label = "pipetaskInit"
                report.job_state_counts[wms_state] += 1
                report.jobs.append(job_report)
                payload_jobs[job_id] = job_ad
            except KeyError as ex:
                _LOG.error("Job missing key '%s': %s", str(ex), job_ad)
                raise
        elif is_service_job(job_ad):
            _LOG.debug(
                "Found service job: id='%s', name='%s', label='%s', NodeStatus='%s', JobStatus='%s'",
                job_id,
                job_ad["DAGNodeName"],
                job_ad.get("bps_job_label", "MISS"),
                job_ad.get("NodeStatus", "MISS"),
                job_ad.get("JobStatus", "MISS"),
            )
            _add_service_job_specific_info(job_ad, specific_info)

    report.total_number_jobs = len(payload_jobs)
    report.exit_code_summary = _get_exit_code_summary(payload_jobs)
    if specific_info:
        report.specific_info = specific_info

    # Workflow will exit with non-zero DAG_STATUS if problem with
    # any of the wms jobs.  So change FAILED to SUCCEEDED if all
    # payload jobs SUCCEEDED.
    if report.total_number_jobs == report.job_state_counts[WmsStates.SUCCEEDED]:
        report.state = WmsStates.SUCCEEDED

    run_reports = {report.wms_id: report}
    _LOG.debug("_create_detailed_report: run_reports = %s", run_reports)
    return run_reports


def _add_service_job_specific_info(job_ad: dict[str, Any], specific_info: WmsSpecificInfo) -> None:
    """Generate report information for service job.

    Parameters
    ----------
    job_ad : `dict` [`str`, `~typing.Any`]
        Provisioning job information.
    specific_info : `lsst.ctrl.bps.WmsSpecificInfo`
        Where to add message.
    """
    status_details = ""
    job_status = _htc_status_to_wms_state(job_ad)

    # Service jobs in queue are deleted when DAG is done.
    # To get accurate status, need to check other info.
    if (
        job_status == WmsStates.DELETED
        and "Reason" in job_ad
        and (
            "Removed by DAGMan" in job_ad["Reason"]
            or "removed because <OtherJobRemoveRequirements = DAGManJobId =?=" in job_ad["Reason"]
            or "DAG is exiting and writing rescue file." in job_ad["Reason"]
        )
    ):
        if "HoldReason" in job_ad:
            # HoldReason exists even if released, so check.
            if "job_released_time" in job_ad and job_ad["job_held_time"] < job_ad["job_released_time"]:
                # If released, assume running until deleted.
                job_status = WmsStates.SUCCEEDED
                status_details = ""
            else:
                # If job held when deleted by DAGMan, still want to
                # report hold reason
                status_details = f"(Job was held for the following reason: {job_ad['HoldReason']})"

        else:
            job_status = WmsStates.SUCCEEDED
    elif job_status == WmsStates.SUCCEEDED:
        status_details = "(Note: Finished before workflow.)"
    elif job_status == WmsStates.HELD:
        status_details = f"({job_ad['HoldReason']})"

    template = "Status of {job_name}: {status} {status_details}"
    context = {
        "job_name": job_ad["DAGNodeName"],
        "status": job_status.name,
        "status_details": status_details,
    }
    specific_info.add_message(template=template, context=context)


def _summary_report(user, hist, pass_thru, schedds=None):
    """Gather run information to be used in generating summary reports.

    Parameters
    ----------
    user : `str`
        Run lookup restricted to given user.
    hist : `float`
        How many previous days to search for run information.
    pass_thru : `str`
        Advanced users can define the HTCondor constraint to be used
        when searching queue and history.

    Returns
    -------
    run_reports : `dict` [`str`, `lsst.ctrl.bps.WmsRunReport`]
        Run information for the summary report.  The keys are HTCondor ids and
        the values are collections of report information for each run.
    message : `str`
        Message to be printed with the summary report.
    """
    # only doing summary report so only look for dagman jobs
    if pass_thru:
        constraint = pass_thru
    else:
        # Notes:
        # * bps_isjob == 'True' isn't getting set for DAG jobs that are
        #   manually restarted.
        # * Any job with DAGManJobID isn't a DAG job
        constraint = 'bps_isjob == "True" && JobUniverse == 7'
        if user:
            constraint += f' && (Owner == "{user}" || bps_operator == "{user}")'

    job_info = condor_search(constraint=constraint, hist=hist, schedds=schedds)

    # Have list of DAGMan jobs, need to get run_report info.
    run_reports = {}
    msg = ""
    for jobs in job_info.values():
        for job_id, job in jobs.items():
            total_jobs, state_counts = _get_state_counts_from_dag_job(job)
            # If didn't get from queue information (e.g., Kerberos bug),
            # try reading from file.
            if total_jobs == 0:
                try:
                    job.update(read_dag_status(job["Iwd"]))
                    total_jobs, state_counts = _get_state_counts_from_dag_job(job)
                except StopIteration:
                    pass  # don't kill report can't find htcondor files

            if "bps_run" not in job:
                _add_run_info(job["Iwd"], job)
            report = WmsRunReport(
                wms_id=job_id,
                global_wms_id=job["GlobalJobId"],
                path=job["Iwd"],
                label=job.get("bps_job_label", "MISS"),
                run=job.get("bps_run", "MISS"),
                project=job.get("bps_project", "MISS"),
                campaign=job.get("bps_campaign", "MISS"),
                payload=job.get("bps_payload", "MISS"),
                operator=_get_owner(job),
                run_summary=_get_run_summary(job),
                state=_htc_status_to_wms_state(job),
                jobs=[],
                total_number_jobs=total_jobs,
                job_state_counts=state_counts,
            )
            run_reports[report.global_wms_id] = report

    return run_reports, msg


def _add_run_info(wms_path, job):
    """Find BPS run information elsewhere for runs without bps attributes.

    Parameters
    ----------
    wms_path : `str`
        Path to submit files for the run.
    job : `dict` [`str`, `~typing.Any`]
        HTCondor dag job information.

    Raises
    ------
    StopIteration
        If cannot find file it is looking for.  Permission errors are
        caught and job's run is marked with error.
    """
    path = Path(wms_path) / "jobs"
    try:
        subfile = next(path.glob("**/*.sub"))
    except (StopIteration, PermissionError):
        job["bps_run"] = "Unavailable"
    else:
        _LOG.debug("_add_run_info: subfile = %s", subfile)
        try:
            with open(subfile, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("+bps_"):
                        m = re.match(r"\+(bps_[^\s]+)\s*=\s*(.+)$", line)
                        if m:
                            _LOG.debug("Matching line: %s", line)
                            job[m.group(1)] = m.group(2).replace('"', "")
                        else:
                            _LOG.debug("Could not parse attribute: %s", line)
        except PermissionError:
            job["bps_run"] = "PermissionError"
    _LOG.debug("After adding job = %s", job)


def _get_owner(job):
    """Get the owner of a dag job.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor dag job information.

    Returns
    -------
    owner : `str`
        Owner of the dag job.
    """
    owner = job.get("bps_operator", None)
    if not owner:
        owner = job.get("Owner", None)
        if not owner:
            _LOG.warning("Could not get Owner from htcondor job: %s", job)
            owner = "MISS"
    return owner


def _get_run_summary(job):
    """Get the run summary for a job.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor dag job information.

    Returns
    -------
    summary : `str`
        Number of jobs per PipelineTask label in approximate pipeline order.
        Format: <label>:<count>[;<label>:<count>]+
    """
    summary = job.get("bps_job_summary", job.get("bps_run_summary", None))
    if not summary:
        summary, _, _ = summarize_dag(job["Iwd"])
        if not summary:
            _LOG.warning("Could not get run summary for htcondor job: %s", job)
    _LOG.debug("_get_run_summary: summary=%s", summary)

    # Workaround sometimes using init vs pipetaskInit
    summary = summary.replace("init:", "pipetaskInit:")

    if "pegasus_version" in job and "pegasus" not in summary:
        summary += ";pegasus:0"

    return summary


def _get_exit_code_summary(jobs):
    """Get the exit code summary for a run.

    Parameters
    ----------
    jobs : `dict` [`str`, `dict` [`str`, Any]]
        Mapping HTCondor job id to job information.

    Returns
    -------
    summary : `dict` [`str`, `list` [`int`]]
        Jobs' exit codes per job label.
    """
    summary = {}
    for job_id, job_ad in jobs.items():
        job_label = job_ad["bps_job_label"]
        summary.setdefault(job_label, [])
        try:
            exit_code = 0
            job_status = job_ad["JobStatus"]
            match job_status:
                case htcondor.JobStatus.COMPLETED | htcondor.JobStatus.HELD:
                    exit_code = job_ad["ExitSignal"] if job_ad["ExitBySignal"] else job_ad["ExitCode"]
                case (
                    htcondor.JobStatus.IDLE
                    | htcondor.JobStatus.RUNNING
                    | htcondor.JobStatus.REMOVED
                    | htcondor.JobStatus.TRANSFERRING_OUTPUT
                    | htcondor.JobStatus.SUSPENDED
                ):
                    pass
                case _:
                    _LOG.debug("Unknown 'JobStatus' value ('%d') in classad for job '%s'", job_status, job_id)
            if exit_code != 0:
                summary[job_label].append(exit_code)
        except KeyError as ex:
            _LOG.debug("Attribute '%s' not found in the classad for job '%s'", ex, job_id)
    return summary


def _get_state_counts_from_jobs(
    wms_workflow_id: str, jobs: dict[str, dict[str, Any]]
) -> tuple[int, dict[WmsStates, int]]:
    """Count number of jobs per WMS state.

    The workflow job and the service jobs are excluded from the count.

    Parameters
    ----------
    wms_workflow_id : `str`
        HTCondor job id.
    jobs : `dict [`dict` [`str`, `~typing.Any`]]
        HTCondor dag job information.

    Returns
    -------
    total_count : `int`
        Total number of dag nodes.
    state_counts : `dict` [`lsst.ctrl.bps.WmsStates`, `int`]
        Keys are the different WMS states and values are counts of jobs
        that are in that WMS state.
    """
    state_counts = dict.fromkeys(WmsStates, 0)
    for job_id, job_ad in jobs.items():
        if job_id != wms_workflow_id and job_ad.get("wms_node_type", WmsNodeType.UNKNOWN) in [
            WmsNodeType.PAYLOAD,
            WmsNodeType.FINAL,
        ]:
            state_counts[_htc_status_to_wms_state(job_ad)] += 1
    total_count = sum(state_counts.values())

    return total_count, state_counts


def _get_state_counts_from_dag_job(job):
    """Count number of jobs per WMS state.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor dag job information.

    Returns
    -------
    total_count : `int`
        Total number of dag nodes.
    state_counts : `dict` [`lsst.ctrl.bps.WmsStates`, `int`]
        Keys are the different WMS states and values are counts of jobs
        that are in that WMS state.
    """
    _LOG.debug("_get_state_counts_from_dag_job: job = %s %s", type(job), len(job))
    state_counts = dict.fromkeys(WmsStates, 0)
    if "DAG_NodesReady" in job:
        state_counts = {
            WmsStates.UNREADY: job.get("DAG_NodesUnready", 0),
            WmsStates.READY: job.get("DAG_NodesReady", 0),
            WmsStates.HELD: job.get("DAG_JobsHeld", 0),
            WmsStates.SUCCEEDED: job.get("DAG_NodesDone", 0),
            WmsStates.FAILED: job.get("DAG_NodesFailed", 0),
            WmsStates.PRUNED: job.get("DAG_NodesFutile", 0),
            WmsStates.MISFIT: job.get("DAG_NodesPre", 0) + job.get("DAG_NodesPost", 0),
        }
        total_jobs = job.get("DAG_NodesTotal")
        _LOG.debug("_get_state_counts_from_dag_job: from DAG_* keys, total_jobs = %s", total_jobs)
    elif "NodesFailed" in job:
        state_counts = {
            WmsStates.UNREADY: job.get("NodesUnready", 0),
            WmsStates.READY: job.get("NodesReady", 0),
            WmsStates.HELD: job.get("JobProcsHeld", 0),
            WmsStates.SUCCEEDED: job.get("NodesDone", 0),
            WmsStates.FAILED: job.get("NodesFailed", 0),
            WmsStates.PRUNED: job.get("NodesFutile", 0),
            WmsStates.MISFIT: job.get("NodesPre", 0) + job.get("NodesPost", 0),
        }
        try:
            total_jobs = job.get("NodesTotal")
        except KeyError as ex:
            _LOG.error("Job missing %s. job = %s", str(ex), job)
            raise
        _LOG.debug("_get_state_counts_from_dag_job: from NODES* keys, total_jobs = %s", total_jobs)
    else:
        # With Kerberos job auth and Kerberos bug, if warning would be printed
        # for every DAG.
        _LOG.debug("Can't get job state counts %s", job["Iwd"])
        total_jobs = 0

    _LOG.debug("total_jobs = %s, state_counts: %s", total_jobs, state_counts)
    return total_jobs, state_counts


def _htc_status_to_wms_state(job):
    """Convert HTCondor job status to generic wms state.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor job information.

    Returns
    -------
    wms_state : `WmsStates`
        The equivalent WmsState to given job's status.
    """
    wms_state = WmsStates.MISFIT
    if "JobStatus" in job:
        wms_state = _htc_job_status_to_wms_state(job)

    if wms_state == WmsStates.MISFIT and "NodeStatus" in job:
        wms_state = _htc_node_status_to_wms_state(job)
    return wms_state


def _htc_job_status_to_wms_state(job):
    """Convert HTCondor job status to generic wms state.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor job information.

    Returns
    -------
    wms_state : `lsst.ctrl.bps.WmsStates`
        The equivalent WmsState to given job's status.
    """
    _LOG.debug(
        "htc_job_status_to_wms_state: %s=%s, %s", job["ClusterId"], job["JobStatus"], type(job["JobStatus"])
    )
    wms_state = WmsStates.MISFIT
    if "JobStatus" in job and job["JobStatus"]:
        job_status = int(job["JobStatus"])

        _LOG.debug("htc_job_status_to_wms_state: job_status = %s", job_status)
        if job_status == htcondor.JobStatus.IDLE:
            wms_state = WmsStates.PENDING
        elif job_status == htcondor.JobStatus.RUNNING:
            wms_state = WmsStates.RUNNING
        elif job_status == htcondor.JobStatus.REMOVED:
            wms_state = WmsStates.DELETED
        elif job_status == htcondor.JobStatus.COMPLETED:
            if (
                (job.get("ExitBySignal", False) and job.get("ExitSignal", 0))
                or job.get("ExitCode", 0)
                or job.get("DAG_Status", 0)
            ):
                wms_state = WmsStates.FAILED
            else:
                wms_state = WmsStates.SUCCEEDED
        elif job_status == htcondor.JobStatus.HELD:
            wms_state = WmsStates.HELD

    return wms_state


def _htc_node_status_to_wms_state(job):
    """Convert HTCondor node status to generic wms state.

    Parameters
    ----------
    job : `dict` [`str`, `~typing.Any`]
        HTCondor job information.

    Returns
    -------
    wms_state : `lsst.ctrl.bps.WmsStates`
        The equivalent WmsState to given node's status.
    """
    wms_state = WmsStates.MISFIT
    match job["NodeStatus"]:
        case NodeStatus.NOT_READY:
            wms_state = WmsStates.UNREADY
        case NodeStatus.READY:
            wms_state = WmsStates.READY
        case NodeStatus.PRERUN:
            wms_state = WmsStates.MISFIT
        case NodeStatus.SUBMITTED:
            if job["JobProcsHeld"]:
                wms_state = WmsStates.HELD
            elif job["StatusDetails"] == "not_idle":
                wms_state = WmsStates.RUNNING
            elif job["JobProcsQueued"]:
                wms_state = WmsStates.PENDING
        case NodeStatus.POSTRUN:
            wms_state = WmsStates.MISFIT
        case NodeStatus.DONE:
            wms_state = WmsStates.SUCCEEDED
        case NodeStatus.ERROR:
            # Use job exit status instead of post script exit status.
            if "DAGMAN error 0" in job["StatusDetails"]:
                wms_state = WmsStates.SUCCEEDED
            elif "ULOG_JOB_ABORTED" in job["StatusDetails"]:
                wms_state = WmsStates.DELETED
            else:
                wms_state = WmsStates.FAILED
        case NodeStatus.FUTILE:
            wms_state = WmsStates.PRUNED
    return wms_state


def _update_jobs(jobs1, jobs2):
    """Update jobs1 with info in jobs2.

    (Basically an update for nested dictionaries.)

    Parameters
    ----------
    jobs1 : `dict` [`str`, `dict` [`str`, `~typing.Any`]]
        HTCondor job information to be updated.
    jobs2 : `dict` [`str`, `dict` [`str`, `~typing.Any`]]
        Additional HTCondor job information.
    """
    for job_id, job_ad in jobs2.items():
        if job_id in jobs1:
            jobs1[job_id].update(job_ad)
        else:
            jobs1[job_id] = job_ad


def _wms_id_type(wms_id):
    """Determine the type of the WMS id.

    Parameters
    ----------
    wms_id : `str`
        WMS id identifying a job.

    Returns
    -------
    id_type : `lsst.ctrl.bps.htcondor.WmsIdType`
        Type of WMS id.
    """
    try:
        int(float(wms_id))
    except ValueError:
        wms_path = Path(wms_id)
        if wms_path.is_dir():
            id_type = WmsIdType.PATH
        else:
            id_type = WmsIdType.GLOBAL
    except TypeError:
        id_type = WmsIdType.UNKNOWN
    else:
        id_type = WmsIdType.LOCAL
    return id_type


def _wms_id_to_cluster(wms_id):
    """Convert WMS id to cluster id.

    Parameters
    ----------
    wms_id : `int` or `float` or `str`
        HTCondor job id or path.

    Returns
    -------
    schedd_ad : `classad.ClassAd`
        ClassAd describing the scheduler managing the job with the given id.
    cluster_id : `int`
        HTCondor cluster id.
    id_type : `lsst.ctrl.bps.wms.htcondor.IdType`
        The type of the provided id.
    """
    coll = htcondor.Collector()

    schedd_ad = None
    cluster_id = None
    id_type = _wms_id_type(wms_id)
    if id_type == WmsIdType.LOCAL:
        schedd_ad = coll.locate(htcondor.DaemonTypes.Schedd)
        cluster_id = int(float(wms_id))
    elif id_type == WmsIdType.GLOBAL:
        constraint = f'GlobalJobId == "{wms_id}"'
        schedd_ads = {ad["Name"]: ad for ad in coll.locateAll(htcondor.DaemonTypes.Schedd)}
        schedds = {name: htcondor.Schedd(ad) for name, ad in schedd_ads.items()}
        job_info = condor_q(constraint=constraint, schedds=schedds)
        if job_info:
            schedd_name, job_rec = job_info.popitem()
            job_id, _ = job_rec.popitem()
            schedd_ad = schedd_ads[schedd_name]
            cluster_id = int(float(job_id))
    elif id_type == WmsIdType.PATH:
        try:
            job_info = read_dag_info(wms_id)
        except (FileNotFoundError, PermissionError, OSError):
            pass
        else:
            schedd_name, job_rec = job_info.popitem()
            job_id, _ = job_rec.popitem()
            schedd_ad = coll.locate(htcondor.DaemonTypes.Schedd, schedd_name)
            cluster_id = int(float(job_id))
    else:
        pass
    return schedd_ad, cluster_id, id_type


def _wms_id_to_dir(wms_id):
    """Convert WMS id to a submit directory candidate.

    The function does not check if the directory exists or if it is a valid
    BPS submit directory.

    Parameters
    ----------
    wms_id : `int` or `float` or `str`
        HTCondor job id or path.

    Returns
    -------
    wms_path : `pathlib.Path` or None
        Submit directory candidate for the run with the given job id. If no
        directory can be associated with the provided WMS id, it will be set
        to None.
    id_type : `lsst.ctrl.bps.wms.htcondor.IdType`
        The type of the provided id.

    Raises
    ------
    TypeError
        Raised if provided WMS id has invalid type.
    """
    coll = htcondor.Collector()
    schedd_ads = []

    constraint = None
    wms_path = None
    id_type = _wms_id_type(wms_id)
    match id_type:
        case WmsIdType.LOCAL:
            constraint = f"ClusterId == {int(float(wms_id))}"
            schedd_ads.append(coll.locate(htcondor.DaemonTypes.Schedd))
        case WmsIdType.GLOBAL:
            constraint = f'GlobalJobId == "{wms_id}"'
            schedd_ads.extend(coll.locateAll(htcondor.DaemonTypes.Schedd))
        case WmsIdType.PATH:
            wms_path = Path(wms_id).resolve()
        case WmsIdType.UNKNOWN:
            raise TypeError(f"Invalid job id type: {wms_id}")
    if constraint is not None:
        schedds = {ad["name"]: htcondor.Schedd(ad) for ad in schedd_ads}
        job_info = condor_history(constraint=constraint, schedds=schedds, projection=["Iwd"])
        if job_info:
            _, job_rec = job_info.popitem()
            _, job_ad = job_rec.popitem()
            wms_path = Path(job_ad["Iwd"])
    return wms_path, id_type


def _create_periodic_release_expr(
    memory: int, multiplier: float | None, limit: int, additional_expr: str = ""
) -> str:
    """Construct an HTCondorAd expression for releasing held jobs.

    Parameters
    ----------
    memory : `int`
        Requested memory in MB.
    multiplier : `float` or None
        Memory growth rate between retries.
    limit : `int`
        Memory limit.
    additional_expr : `str`, optional
        Expression to add to periodic_release.  Defaults to empty string.

    Returns
    -------
    expr : `str`
        A string representing an HTCondor ClassAd expression for releasing job.
    """
    _LOG.debug(
        "periodic_release: memory: %s, multiplier: %s, limit: %s, additional_expr: %s",
        memory,
        multiplier,
        limit,
        additional_expr,
    )

    # ctrl_bps sets multiplier to None in the GenericWorkflow if
    # memoryMultiplier <= 1, but checking value just in case.
    if (not multiplier or multiplier <= 1) and not additional_expr:
        return ""

    # Job ClassAds attributes 'HoldReasonCode' and 'HoldReasonSubCode' are
    # UNDEFINED if job is not HELD (i.e. when 'JobStatus' is not 5).
    # The special comparison operators ensure that all comparisons below will
    # evaluate to FALSE in this case.
    #
    # Note:
    # May not be strictly necessary. Operators '&&' and '||' are not strict so
    # the entire expression should evaluate to FALSE when the job is not HELD.
    # According to ClassAd evaluation semantics FALSE && UNDEFINED is FALSE,
    # but better safe than sorry.
    is_held = "JobStatus == 5"
    is_retry_allowed = "NumJobStarts <= JobMaxRetries"

    mem_expr = ""
    if memory and multiplier and multiplier > 1 and limit:
        was_mem_exceeded = (
            "(HoldReasonCode =?= 34 && HoldReasonSubCode =?= 0 "
            "|| HoldReasonCode =?= 3 && HoldReasonSubCode =?= 34)"
        )
        was_below_limit = f"min({{int({memory} * pow({multiplier}, NumJobStarts - 1)), {limit}}}) < {limit}"
        mem_expr = f"{was_mem_exceeded} && {was_below_limit}"

    user_expr = ""
    if additional_expr:
        # Never auto release a job held by user.
        user_expr = f"HoldReasonCode =!= 1 && {additional_expr}"

    expr = f"{is_held} && {is_retry_allowed}"
    if user_expr and mem_expr:
        expr += f" && ({mem_expr} || {user_expr})"
    elif user_expr:
        expr += f" && {user_expr}"
    elif mem_expr:
        expr += f" && {mem_expr}"

    return expr


def _create_periodic_remove_expr(memory, multiplier, limit):
    """Construct an HTCondorAd expression for removing jobs from the queue.

    Parameters
    ----------
    memory : `int`
        Requested memory in MB.
    multiplier : `float`
        Memory growth rate between retries.
    limit : `int`
        Memory limit.

    Returns
    -------
    expr : `str`
        A string representing an HTCondor ClassAd expression for removing jobs.
    """
    # Job ClassAds attributes 'HoldReasonCode' and 'HoldReasonSubCode'
    # are UNDEFINED if job is not HELD (i.e. when 'JobStatus' is not 5).
    # The special comparison operators ensure that all comparisons below
    # will evaluate to FALSE in this case.
    #
    # Note:
    # May not be strictly necessary. Operators '&&' and '||' are not
    # strict so the entire expression should evaluate to FALSE when the
    # job is not HELD. According to ClassAd evaluation semantics
    # FALSE && UNDEFINED is FALSE, but better safe than sorry.
    is_held = "JobStatus == 5"
    is_retry_disallowed = "NumJobStarts > JobMaxRetries"

    mem_expr = ""
    if memory and multiplier and multiplier > 1 and limit:
        mem_limit_expr = f"min({{int({memory} * pow({multiplier}, NumJobStarts - 1)), {limit}}}) == {limit}"

        mem_expr = (  # Add || here so only added if adding memory expr
            " || ((HoldReasonCode =?= 34 && HoldReasonSubCode =?= 0 "
            f"|| HoldReasonCode =?= 3 && HoldReasonSubCode =?= 34) && {mem_limit_expr})"
        )

    expr = f"{is_held} && ({is_retry_disallowed}{mem_expr})"
    return expr


def _create_request_memory_expr(memory, multiplier, limit):
    """Construct an HTCondor ClassAd expression for safe memory scaling.

    Parameters
    ----------
    memory : `int`
        Requested memory in MB.
    multiplier : `float`
        Memory growth rate between retries.
    limit : `int`
        Memory limit.

    Returns
    -------
    expr : `str`
        A string representing an HTCondor ClassAd expression enabling safe
        memory scaling between job retries.
    """
    # The check if the job was held due to exceeding memory requirements
    # will be made *after* job was released back to the job queue (is in
    # the IDLE state), hence the need to use `Last*` job ClassAds instead of
    # the ones describing job's current state.
    #
    # Also, 'Last*' job ClassAds attributes are UNDEFINED when a job is
    # initially put in the job queue. The special comparison operators ensure
    # that all comparisons below will evaluate to FALSE in this case.
    was_mem_exceeded = (
        "LastJobStatus =?= 5 "
        "&& (LastHoldReasonCode =?= 34 && LastHoldReasonSubCode =?= 0 "
        "|| LastHoldReasonCode =?= 3 && LastHoldReasonSubCode =?= 34)"
    )

    # If job runs the first time or was held for reasons other than exceeding
    # the memory, set the required memory to the requested value or use
    # the memory value measured by HTCondor (MemoryUsage) depending on
    # whichever is greater.
    expr = (
        f"({was_mem_exceeded}) "
        f"? min({{int({memory} * pow({multiplier}, NumJobStarts)), {limit}}}) "
        f": max({{{memory}, MemoryUsage ?: 0}})"
    )
    return expr


def _locate_schedds(locate_all=False):
    """Find out Scheduler daemons in an HTCondor pool.

    Parameters
    ----------
    locate_all : `bool`, optional
        If True, all available schedulers in the HTCondor pool will be located.
        False by default which means that the search will be limited to looking
        for the Scheduler running on a local host.

    Returns
    -------
    schedds : `dict` [`str`, `htcondor.Schedd`]
        A mapping between Scheduler names and Python objects allowing for
        interacting with them.
    """
    coll = htcondor.Collector()

    schedd_ads = []
    if locate_all:
        schedd_ads.extend(coll.locateAll(htcondor.DaemonTypes.Schedd))
    else:
        schedd_ads.append(coll.locate(htcondor.DaemonTypes.Schedd))
    return {ad["Name"]: htcondor.Schedd(ad) for ad in schedd_ads}


def _gather_site_values(config, compute_site):
    """Gather values specific to given site.

    Parameters
    ----------
    config : `lsst.ctrl.bps.BpsConfig`
        BPS configuration that includes necessary submit/runtime
        information.
    compute_site : `str`
        Compute site name.

    Returns
    -------
    site_values : `dict` [`str`, `~typing.Any`]
        Values specific to the given site.
    """
    site_values = {"attrs": {}, "profile": {}}
    search_opts = {}
    if compute_site:
        search_opts["curvals"] = {"curr_site": compute_site}

    # Determine the hard limit for the memory requirement.
    found, limit = config.search("memoryLimit", opt=search_opts)
    if not found:
        search_opts["default"] = DEFAULT_HTC_EXEC_PATT
        _, patt = config.search("executeMachinesPattern", opt=search_opts)
        del search_opts["default"]

        # To reduce the amount of data, ignore dynamic slots (if any) as,
        # by definition, they cannot have more memory than
        # the partitionable slot they are the part of.
        constraint = f'SlotType != "Dynamic" && regexp("{patt}", Machine)'
        pool_info = condor_status(constraint=constraint)
        try:
            limit = max(int(info["TotalSlotMemory"]) for info in pool_info.values())
        except ValueError:
            _LOG.debug("No execute machine in the pool matches %s", patt)
    if limit:
        config[".bps_defined.memory_limit"] = limit

    _, site_values["bpsUseShared"] = config.search("bpsUseShared", opt={"default": False})
    site_values["memoryLimit"] = limit

    found, value = config.search("accountingGroup", opt=search_opts)
    if found:
        site_values["accountingGroup"] = value
    found, value = config.search("accountingUser", opt=search_opts)
    if found:
        site_values["accountingUser"] = value

    key = f".site.{compute_site}.profile.condor"
    if key in config:
        for subkey, val in config[key].items():
            if subkey.startswith("+"):
                site_values["attrs"][subkey[1:]] = val
            else:
                site_values["profile"][subkey] = val

    return site_values


def _gather_label_values(config: BpsConfig, label: str) -> dict[str, Any]:
    """Gather values specific to given job label.

    Parameters
    ----------
    config : `lsst.ctrl.bps.BpsConfig`
        BPS configuration that includes necessary submit/runtime
        information.
    label : `str`
        GenericWorkflowJob label.

    Returns
    -------
    values : `dict` [`str`, `~typing.Any`]
        Values specific to the given job label.
    """
    values: dict[str, Any] = {"attrs": {}, "profile": {}}

    search_opts = {}
    profile_key = ""
    if label == "finalJob":
        search_opts["searchobj"] = config["finalJob"]
        profile_key = ".finalJob.profile.condor"
    elif label in config["cluster"]:
        search_opts["curvals"] = {"curr_cluster": label}
        profile_key = f".cluster.{label}.profile.condor"
    elif label in config["pipetask"]:
        search_opts["curvals"] = {"curr_pipetask": label}
        profile_key = f".pipetask.{label}.profile.condor"

    found, value = config.search("releaseExpr", opt=search_opts)
    if found:
        values["releaseExpr"] = value

    found, value = config.search("overwriteJobFiles", opt=search_opts)
    if found:
        values["overwriteJobFiles"] = value
    else:
        values["overwriteJobFiles"] = True

    if profile_key and profile_key in config:
        for subkey, val in config[profile_key].items():
            if subkey.startswith("+"):
                values["attrs"][subkey[1:]] = val
            else:
                values["profile"][subkey] = val

    return values


def is_service_job(job_ad: dict[str, Any]) -> bool:
    """Determine if a job is a service one.

    Parameters
    ----------
    job_ad : `dict` [`str`, Any]
        Information about an HTCondor job.

    Returns
    -------
    is_service_job : `bool`
        True if the job is a service one, false otherwise.

    Notes
    -----
    At the moment, HTCondor does not provide a native way to distinguish
    between payload and service jobs in the workflow.  This code depends
    on read_node_status adding wms_node_type.
    """
    return job_ad.get("wms_node_type", WmsNodeType.UNKNOWN) == WmsNodeType.SERVICE


def _group_to_subdag(
    config: BpsConfig, generic_workflow_group: GenericWorkflowGroup, out_prefix: str
) -> HTCJob:
    """Convert a generic workflow group to an HTCondor dag.

    Parameters
    ----------
    config : `lsst.ctrl.bps.BpsConfig`
        Workflow configuration.
    generic_workflow_group : `lsst.ctrl.bps.GenericWorkflowGroup`
        The generic workflow group to convert.
    out_prefix : `str`
        Location prefix to be used when creating jobs.

    Returns
    -------
    htc_job : `lsst.ctrl.bps.htcondor.HTCJob`
        Job for running the HTCondor dag.
    """
    jobname = f"wms_{generic_workflow_group.name}"
    htc_job = HTCJob(name=jobname, label=generic_workflow_group.label)
    htc_job.add_dag_cmds({"dir": f"subdags/{jobname}"})
    htc_job.subdag = _generic_workflow_to_htcondor_dag(config, generic_workflow_group, out_prefix)
    if not generic_workflow_group.blocking:
        htc_job.dagcmds["post"] = {
            "defer": "",
            "executable": f"{os.path.dirname(__file__)}/subdag_post.sh",
            "arguments": f"{jobname} $RETURN",
        }
    return htc_job


def _create_check_job(group_job_name: str, job_label: str) -> HTCJob:
    """Create a job to check status of a group job.

    Parameters
    ----------
    group_job_name : `str`
        Name of the group job.
    job_label : `str`
        Label to use for the check status job.

    Returns
    -------
    htc_job : `lsst.ctrl.bps.htcondor.HTCJob`
        Job description for the job to check group job status.
    """
    htc_job = HTCJob(name=f"wms_check_status_{group_job_name}", label=job_label)
    htc_job.subfile = "${CTRL_BPS_HTCONDOR_DIR}/python/lsst/ctrl/bps/htcondor/check_group_status.sub"
    htc_job.add_dag_cmds({"dir": f"subdags/{group_job_name}", "vars": {"group_job_name": group_job_name}})

    return htc_job


def _generic_workflow_to_htcondor_dag(
    config: BpsConfig, generic_workflow: GenericWorkflow, out_prefix: str
) -> HTCDag:
    """Convert a GenericWorkflow to a HTCDag.

    Parameters
    ----------
    config : `lsst.ctrl.bps.BpsConfig`
        Workflow configuration.
    generic_workflow : `lsst.ctrl.bps.GenericWorkflow`
        The GenericWorkflow to convert.
    out_prefix : `str`
        Location prefix where the HTCondor files will be written.

    Returns
    -------
    dag : `lsst.ctrl.bps.htcondor.HTCDag`
        The HTCDag representation of the given GenericWorkflow.
    """
    dag = HTCDag(name=generic_workflow.name)

    _LOG.debug("htcondor dag attribs %s", generic_workflow.run_attrs)
    dag.add_attribs(generic_workflow.run_attrs)
    dag.add_attribs(
        {
            "bps_run_quanta": create_count_summary(generic_workflow.quanta_counts),
            "bps_job_summary": create_count_summary(generic_workflow.job_counts),
        }
    )

    _, tmp_template = config.search("subDirTemplate", opt={"replaceVars": False, "default": ""})
    if isinstance(tmp_template, str):
        subdir_template = defaultdict(lambda: tmp_template)
    else:
        subdir_template = tmp_template

    # Create all DAG jobs
    site_values = {}  # Cache compute site specific values to reduce config lookups.
    cached_values = {}  # Cache label-specific values to reduce config lookups.
    # Note: Can't use get_job_by_label because those only include payload jobs.
    for job_name in generic_workflow:
        gwjob = generic_workflow.get_job(job_name)
        if gwjob.node_type == GenericWorkflowNodeType.PAYLOAD:
            gwjob = cast(GenericWorkflowJob, gwjob)
            if gwjob.compute_site not in site_values:
                site_values[gwjob.compute_site] = _gather_site_values(config, gwjob.compute_site)
            if gwjob.label not in cached_values:
                cached_values[gwjob.label] = deepcopy(site_values[gwjob.compute_site])
                cached_values[gwjob.label].update(_gather_label_values(config, gwjob.label))
                _LOG.debug("cached: %s= %s", gwjob.label, cached_values[gwjob.label])
            htc_job = _create_job(
                subdir_template[gwjob.label],
                cached_values[gwjob.label],
                generic_workflow,
                gwjob,
                out_prefix,
            )
        elif gwjob.node_type == GenericWorkflowNodeType.NOOP:
            gwjob = cast(GenericWorkflowNoopJob, gwjob)
            htc_job = HTCJob(f"wms_{gwjob.name}", label=gwjob.label)
            htc_job.subfile = "${CTRL_BPS_HTCONDOR_DIR}/python/lsst/ctrl/bps/htcondor/noop.sub"
            htc_job.add_job_attrs({"bps_job_name": gwjob.name, "bps_job_label": gwjob.label})
            htc_job.add_dag_cmds({"noop": True})
        elif gwjob.node_type == GenericWorkflowNodeType.GROUP:
            gwjob = cast(GenericWorkflowGroup, gwjob)
            htc_job = _group_to_subdag(config, gwjob, out_prefix)
            # In case DAGMAN_GENERATE_SUBDAG_SUBMITS is False,
            dag.graph["submit_options"]["do_recurse"] = True
        else:
            raise RuntimeError(f"Unsupported generic workflow node type {gwjob.node_type} ({gwjob.name})")
        _LOG.debug("Calling adding job %s %s", htc_job.name, htc_job.label)
        dag.add_job(htc_job)

    # Add job dependencies to the DAG (be careful with wms_ jobs)
    for job_name in generic_workflow:
        gwjob = generic_workflow.get_job(job_name)
        parent_name = (
            gwjob.name if gwjob.node_type == GenericWorkflowNodeType.PAYLOAD else f"wms_{gwjob.name}"
        )
        successor_jobs = [generic_workflow.get_job(j) for j in generic_workflow.successors(job_name)]
        children_names = []
        if gwjob.node_type == GenericWorkflowNodeType.GROUP:
            gwjob = cast(GenericWorkflowGroup, gwjob)
            group_children = []  # Dependencies between same group jobs
            for sjob in successor_jobs:
                if sjob.node_type == GenericWorkflowNodeType.GROUP and sjob.label == gwjob.label:
                    group_children.append(f"wms_{sjob.name}")
                elif sjob.node_type == GenericWorkflowNodeType.PAYLOAD:
                    children_names.append(sjob.name)
                else:
                    children_names.append(f"wms_{sjob.name}")
            if group_children:
                dag.add_job_relationships([parent_name], group_children)
            if not gwjob.blocking:
                # Since subdag will always succeed, need to add a special
                # job that fails if group failed to block payload children.
                check_job = _create_check_job(f"wms_{gwjob.name}", gwjob.label)
                dag.add_job(check_job)
                dag.add_job_relationships([f"wms_{gwjob.name}"], [check_job.name])
                parent_name = check_job.name
        else:
            for sjob in successor_jobs:
                if sjob.node_type == GenericWorkflowNodeType.PAYLOAD:
                    children_names.append(sjob.name)
                else:
                    children_names.append(f"wms_{sjob.name}")

        dag.add_job_relationships([parent_name], children_names)

    # If final job exists in generic workflow, create DAG final job
    final = generic_workflow.get_final()
    if final and isinstance(final, GenericWorkflowJob):
        if final.compute_site and final.compute_site not in site_values:
            site_values[final.compute_site] = _gather_site_values(config, final.compute_site)
        if final.label not in cached_values:
            cached_values[final.label] = deepcopy(site_values[final.compute_site])
            cached_values[final.label].update(_gather_label_values(config, final.label))
        final_htjob = _create_job(
            subdir_template[final.label],
            cached_values[final.label],
            generic_workflow,
            final,
            out_prefix,
        )
        if "post" not in final_htjob.dagcmds:
            final_htjob.dagcmds["post"] = {
                "defer": "",
                "executable": f"{os.path.dirname(__file__)}/final_post.sh",
                "arguments": f"{final.name} $DAG_STATUS $RETURN",
            }
        dag.add_final_job(final_htjob)
    elif final and isinstance(final, GenericWorkflow):
        raise NotImplementedError("HTCondor plugin does not support a workflow as the final job")
    elif final:
        raise TypeError(f"Invalid type for GenericWorkflow.get_final() results ({type(final)})")

    return dag
