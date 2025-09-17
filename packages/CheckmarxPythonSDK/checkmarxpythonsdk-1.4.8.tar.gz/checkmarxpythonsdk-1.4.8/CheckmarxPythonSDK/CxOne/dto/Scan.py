# encoding: utf-8
from typing import List
from .StatusDetails import StatusDetails


class Scan(object):
    def __init__(self, scan_id, status, status_details: List[StatusDetails], position_in_queue, project_id,
                 project_name,
                 branch,
                 commit_id, commit_tag,
                 upload_url, created_at, updated_at, user_agent, initiator, tags, metadata, engines=None,
                 source_type=None, source_origin=None):
        """

        Args:
            scan_id (str): The unique identifier of the scan.
            status (str): The execution status of the scan.
                    Enum:[ Queued, Running, Completed, Failed, Partial, Canceled ]
            status_details (`list` of `StatusDetails`):
            position_in_queue (int): the position of the scan in the execution queue.
            project_id (str): The associated project id
            project_name (str):
            branch (str): The git branch
            commit_id (str): The git commit id. Mutually exclusive to commitTag
            commit_tag (str): The git tag. Mutually exclusive to commitId
            upload_url (str): The URL pointing to the location of the uploaded file that was scanned.
            created_at (str): The date and time that the scan was created.
            updated_at (str): The date and time that the scan was created.
            user_agent (str): The user-agent header of the tool/platform that initiated the scan
            initiator (str): An identifier of the user who created the scan.
            tags (dict): An object representing the scan tags in a key-value format
            metadata (dict): A JSON object containing info about the scan settings.
        """
        self.id = scan_id
        self.status = status
        self.statusDetails = status_details
        self.positionInQueue = position_in_queue
        self.projectId = project_id
        self.projectName = project_name
        self.branch = branch
        self.commitId = commit_id
        self.commitTag = commit_tag
        self.uploadUrl = upload_url
        self.createdAt = created_at
        self.updatedAt = updated_at
        self.userAgent = user_agent
        self.initiator = initiator
        self.tags = tags
        self.metadata = metadata
        self.engines = engines
        self.sourceType = source_type
        self.sourceOrigin = source_origin

    def __str__(self):
        return """Scan(id={}, status={}, statusDetails={}, positionInQueue={}, projectId={}, projectName={}, branch={}, 
        commitId={},
        commitTag={}, uploadUrl={}, createdAt={}, updatedAt={}, userAgent={}, initiator={}, tags={}, 
        metadata={}, engines={}, sourceType={}, sourceOrigin={})""".format(
            self.id,
            self.status,
            self.statusDetails,
            self.positionInQueue,
            self.projectId,
            self.projectName,
            self.branch,
            self.commitId,
            self.commitTag,
            self.uploadUrl,
            self.createdAt,
            self.updatedAt,
            self.userAgent,
            self.initiator,
            self.tags,
            self.metadata,
            self.engines,
            self.sourceType,
            self.sourceOrigin,
        )
