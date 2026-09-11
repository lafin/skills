from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    identifier: str
    attempts: int = 0


def next_action(job: Job, status: int) -> str:
    if 200 <= status < 300:
        return "complete"
    if status in (408, 429) and job.attempts < 3:
        return "retry"
    if 500 <= status < 600 and job.attempts < 2:
        return "retry"
    return "dead-letter"
