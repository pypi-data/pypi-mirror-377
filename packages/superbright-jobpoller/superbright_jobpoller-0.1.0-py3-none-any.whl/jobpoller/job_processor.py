"""
Job processor module for handling job polling and processing
"""

import os
import time
import json
import logging
import requests
from datetime import datetime
from logging.handlers import RotatingFileHandler
import subprocess
from typing import Dict, Any, Optional, Tuple, List, Union, Callable

from .config import JobConfig
from .utils.logger import setup_logger


class JobProcessor:
    """
    Base class for job processing with configurable polling and processing logic
    """
    
    def __init__(
        self,
        config: JobConfig,
        logger_name: str = "JobPoller",
        job_id_key: str = "msgId",
        message_key: str = "message",
        process_script: Optional[Union[str, List[str]]] = None,
        script_executor: Optional[str] = None,
        job_parser: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """
        Initialize the job processor
        
        Args:
            config (JobConfig): Configuration for API and polling settings
            logger_name (str, optional): Name for the logger. Defaults to "JobPoller".
            job_id_key (str, optional): Key for job ID in job data. Defaults to "msgId".
            message_key (str, optional): Key for message in job data. Defaults to "message".
            process_script (Union[str, List[str]], optional): Script to run for processing. Defaults to None.
            script_executor (str, optional): Executor for the script (python, bash, etc). Defaults to None.
            job_parser (Callable, optional): Function to parse job data. Defaults to None.
        """
        self.config = config
        self.job_id_key = job_id_key
        self.message_key = message_key
        self.process_script = process_script
        self.script_executor = script_executor
        self.job_parser = job_parser or self._default_job_parser
        
        # Set up logging
        os.makedirs(config.log_dir, exist_ok=True)
        self.logger = setup_logger(logger_name)
    
    def _default_job_parser(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default job parser that extracts job ID and parses message as JSON
        
        Args:
            job_data (Dict[str, Any]): Raw job data from API
            
        Returns:
            Dict[str, Any]: Parsed job data
        """
        job_id = job_data.get(self.job_id_key)
        message = job_data.get(self.message_key)
        
        if isinstance(message, str):
            try:
                message_data = json.loads(message)
            except json.JSONDecodeError:
                message_data = {"raw_message": message}
        else:
            message_data = message or {}
            
        return {
            "job_id": job_id,
            **message_data
        }
    
    def _make_job_logger(self, job_id: str, **kwargs) -> Tuple[str, logging.Handler]:
        """
        Create a file handler for job-specific logging
        
        Args:
            job_id (str): Job ID
            **kwargs: Additional parameters to include in log filename
            
        Returns:
            Tuple[str, logging.Handler]: Log filename and file handler
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create filename with job_id and any additional parameters
        filename_parts = [f"job_{job_id}"]
        for key, value in kwargs.items():
            if value:
                filename_parts.append(f"{value}")
        
        filename_parts.append(timestamp)
        filename = f"{'_'.join(filename_parts)}.log"
        
        path = os.path.join(self.config.log_dir, filename)
        fh = RotatingFileHandler(path, maxBytes=10**7, backupCount=3)
        fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)
        
        return filename, fh
    
    def poll_for_jobs(self) -> Optional[Dict[str, Any]]:
        """
        Poll for available jobs
        
        Returns:
            Optional[Dict[str, Any]]: Job data if available, None otherwise
        """
        try:
            resp = requests.get(
                f"{self.config.api_url}{self.config.poll_endpoint}", 
                headers=self.config.headers
            )
            
            if resp.status_code == 200:
                return resp.json().get("data")
            elif resp.status_code != 204:
                self.logger.error("Poll error %s: %s", resp.status_code, resp.text)
        except Exception:
            self.logger.exception("Exception while polling")
            
        return None
    
    def mark_job(self, job_id: str, endpoint: str, payload: Dict[str, Any], log_fn: str) -> bool:
        """
        Mark job as completed or failed
        
        Args:
            job_id (str): Job ID
            endpoint (str): API endpoint for marking job
            payload (Dict[str, Any]): Payload to send to API
            log_fn (str): Log filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Uploading assets completed.")
            
            # Read logs
            with open(os.path.join(self.config.log_dir, log_fn), "rb") as f:
                data = f.read()
            
            # Get upload URL
            upload_url_endpoint = self.config.upload_url_endpoint.format(job_id=job_id)
            upload = requests.get(
                f"{self.config.api_url}{upload_url_endpoint}", 
                headers=self.config.headers
            )
            upload.raise_for_status()
            up = upload.json()["data"]
            payload["logs_file_key"] = up["uploadFileKey"]
            
            self.logger.info("Uploading Job Logs.")
            # PUT logs
            put = requests.put(
                up["uploadUrl"], 
                data=data, 
                headers={"Content-Type": "text/plain"}
            )
            put.raise_for_status()
            self.logger.info("Uploading Job Logs completed.")
            
            status = "completed" if "delete" in endpoint else "failed"
            self.logger.info("Marking job %s via %s as %s", job_id, endpoint, status)
            
            resp = requests.put(
                f"{self.config.api_url}{endpoint}", 
                headers=self.config.headers, 
                json=payload
            )
            resp.raise_for_status()
            
            self.logger.info("Marked job %s via %s as %s", job_id, endpoint, status)
            return True
            
        except Exception:
            self.logger.exception("Failed to mark job %s via %s", job_id, endpoint)
            return False
    
    def run_script(self, job_id: str, parsed_job: Dict[str, Any], job_log_fn: str) -> int:
        """
        Run the processing script for a job
        
        Args:
            job_id (str): Job ID
            parsed_job (Dict[str, Any]): Parsed job data
            job_log_fn (str): Log filename
            
        Returns:
            int: Exit code from script
        """
        # Ensure all Python subprocesses flush immediately
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        # Build command based on configuration
        cmd = []
        if self.script_executor:
            cmd.append(self.script_executor)
        
        if isinstance(self.process_script, list):
            cmd.extend(self.process_script)
        elif self.process_script:
            cmd.append(self.process_script)
        else:
            self.logger.error("No process script configured")
            return 1
        
        # Add job parameters as arguments
        for key, value in parsed_job.items():
            if key != "job_id" and value is not None:
                cmd.append(str(value))
        
        self.logger.info(f"Running command: {' '.join(cmd)}")
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,  # line buffering
            text=True,
            env=env,
        )
        
        # Read one line at a time as soon as it's available
        for line in proc.stdout:
            self.logger.info(line.rstrip())
            
        return proc.wait()
    
    def process(self, job: Dict[str, Any]) -> None:
        """
        Process a job
        
        Args:
            job (Dict[str, Any]): Job data from API
        """
        # Parse job data
        parsed_job = self.job_parser(job)
        job_id = parsed_job.get("job_id")
        
        if not job_id:
            self.logger.error("Invalid job data: missing job ID")
            return
        
        # Set up job-specific logger
        log_params = {k: v for k, v in parsed_job.items() if k != "job_id" and v is not None}
        job_log_fn, fh = self._make_job_logger(job_id, **log_params)
        
        try:
            # Run the processing script
            exit_code = self.run_script(job_id, parsed_job, job_log_fn)
            
            if exit_code != 0:
                raise RuntimeError(f"Script failed with code {exit_code}")
            
            # Mark job as completed
            complete_endpoint = self.config.complete_endpoint.format(job_id=job_id)
            payload = {k: v for k, v in parsed_job.items() if k != "job_id"}
            
            if not self.mark_job(job_id, complete_endpoint, payload, job_log_fn):
                raise RuntimeError("Failed to mark job completed")
                
        except Exception as e:
            self.logger.exception("Job %s failed: %s", job_id, e)
            
            # Mark job as failed
            fail_endpoint = self.config.fail_endpoint.format(job_id=job_id)
            payload = {k: v for k, v in parsed_job.items() if k != "job_id"}
            self.mark_job(job_id, fail_endpoint, payload, job_log_fn)
            
        finally:
            # Always remove the file handler so next job gets a fresh one
            self.logger.removeHandler(fh)
            fh.close()
    
    def run(self) -> None:
        """
        Run the job processor in a continuous loop
        """
        self.logger.info(f"{self.__class__.__name__} starting up")
        
        try:
            while True:
                job = self.poll_for_jobs()
                
                if job:
                    self.process(job)
                else:
                    self.logger.info("No jobs; sleeping %s seconds", self.config.poll_interval)
                    time.sleep(self.config.poll_interval)
                    
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
        except Exception:
            self.logger.exception("Fatal error in main loop")
