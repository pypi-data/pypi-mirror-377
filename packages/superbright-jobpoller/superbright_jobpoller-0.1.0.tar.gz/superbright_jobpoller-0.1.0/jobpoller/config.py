"""
Configuration module for JobPoller
"""

class JobConfig:
    """Configuration class for job polling settings"""
    
    def __init__(
        self,
        api_url,
        api_key,
        poll_interval=10,
        log_dir="job_logs",
        poll_endpoint="/jobs/next",
        upload_url_endpoint="/jobs/{job_id}/uploadUrl",
        complete_endpoint="/jobs/{job_id}/delete",
        fail_endpoint="/jobs/{job_id}/archive",
        headers=None
    ):
        """
        Initialize job configuration
        
        Args:
            api_url (str): Base URL for the API
            api_key (str): API key for authentication
            poll_interval (int, optional): Interval between polls in seconds. Defaults to 10.
            log_dir (str, optional): Directory to store logs. Defaults to "job_logs".
            poll_endpoint (str, optional): Endpoint for polling jobs. Defaults to "/jobs/next".
            upload_url_endpoint (str, optional): Endpoint for getting upload URL. Defaults to "/jobs/{job_id}/uploadUrl".
            complete_endpoint (str, optional): Endpoint for marking job as complete. Defaults to "/jobs/{job_id}/delete".
            fail_endpoint (str, optional): Endpoint for marking job as failed. Defaults to "/jobs/{job_id}/archive".
            headers (dict, optional): Custom headers for API requests. Defaults to None.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.log_dir = log_dir
        self.poll_endpoint = poll_endpoint
        self.upload_url_endpoint = upload_url_endpoint
        self.complete_endpoint = complete_endpoint
        self.fail_endpoint = fail_endpoint
        
        if headers is None:
            self.headers = {
                "Authorization": f"ApiKey {api_key}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = headers
