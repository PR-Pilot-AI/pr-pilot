import logging
import os
from pathlib import Path

import yaml
from jinja2 import FileSystemLoader, Environment, select_autoescape
from kubernetes import config
from kubernetes.client import BatchV1Api


logger = logging.getLogger(__name__)


class KubernetesJob:

    def __init__(self, task):
        self.task = task

    def get_image_name(self):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        version_txt_path = Path(os.path.join(parent_dir, "version.txt"))
        version = version_txt_path.read_text().strip()
        return (
            f"us-west2-docker.pkg.dev/darwin-407004/pr-pilot/pr-pilot-worker:{version}"
        )

    def spawn(self):
        # Load kubeconfig
        try:
            config.load_kube_config()
        except config.config_exception.ConfigException:
            config.load_incluster_config()

        # Load the Jinja2 template
        this_dir = os.path.dirname(os.path.abspath(__file__))
        file_loader = FileSystemLoader(this_dir)
        env = Environment(loader=file_loader, autoescape=select_autoescape())
        template = env.get_template("job_template.yaml.j2")
        # Render the template with variables
        github_project_org, github_project_name = self.task.github_project.split("/")
        job_name = "job-" + str(self.task.id)
        rendered_template = template.render(
            job_name=job_name,
            image=self.get_image_name(),
            github_user=self.task.github_user,
            github_project_org=github_project_org,
            github_project_name=github_project_name,
            branch=self.task.branch,
            task_id=str(self.task.id),
        )

        # Load the rendered template as a Kubernetes object
        job_object = yaml.safe_load(rendered_template)
        logger.info(f"Job created: {job_name}")
        # Create the job
        batch_v1 = BatchV1Api()
        return batch_v1.create_namespaced_job(body=job_object, namespace="default")
