"""
AIShield Agent任务发布模块
Agent发布自己解决不了的任务，其他Agent接单
"""
import json, time, uuid
from typing import Dict, List

jobs_db = {}
bids_db = {}

def create_job(publisher_did, title, description, category, reward, deadline=3600):
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job = {
        "id": job_id, "publisher": publisher_did, "title": title,
        "description": description, "category": category, "reward": reward,
        "deadline": int(time.time()) + deadline, "status": "open",
        "bids": [], "created_at": int(time.time())
    }
    jobs_db[job_id] = job
    return job

def list_jobs(status="open", category=None):
    jobs = list(jobs_db.values())
    if status: jobs = [j for j in jobs if j["status"] == status]
    if category: jobs = [j for j in jobs if j["category"] == category]
    return sorted(jobs, key=lambda x: x["created_at"], reverse=True)

def submit_bid(job_id, bidder_did, proposal, estimated_time):
    if job_id not in jobs_db: return {"error": "Job not found"}
    job = jobs_db[job_id]
    if job["status"] != "open": return {"error": f"Job is {job['status']}"}
    bid = {"id": f"bid_{uuid.uuid4().hex[:8]}", "job_id": job_id,
           "bidder": bidder_did, "proposal": proposal,
           "estimated_time": estimated_time, "created_at": int(time.time())}
    job["bids"].append(bid)
    job["status"] = "bidding"
    return bid

def accept_bid(job_id, bid_id):
    if job_id not in jobs_db: return {"error": "Job not found"}
    job = jobs_db[job_id]
    job["status"] = "assigned"
    job["assigned_bid"] = bid_id
    return {"success": True}

def submit_result(job_id, result):
    if job_id not in jobs_db: return {"error": "Job not found"}
    job = jobs_db[job_id]
    job["status"] = "completed"
    job["result"] = result
    job["completed_at"] = int(time.time())
    return {"success": True}
