#!flask/bin/python
from flask import Flask
from flask import abort, current_app, jsonify, make_response, redirect, request, url_for

app = Flask(__name__)

JOB_STATUS = {
    0: 'QUEUED',
    1: 'IN_PROGRESS',
    2: 'DONE',
    3: 'ERROR'
}

queues = [
    {
        'id': 1,
        'name': u'default-queue',
        'jobs': [] 
    }]

jobs = []


''' Queues - methods for creating and deleting queues, retrieving next job to print, rearranging jobs '''

# Displays all queues
@app.route('/3dp-api/queues', methods=['GET'])
def get_queues():
    return jsonify({'queues': [make_public_queue(queue) for queue in queues]})

# Displays info about queue with given ID
@app.route('/3dp-api/queues/<int:queue_id>', methods=['GET'])
def get_queue(queue_id):
    queue = find_queue(queue_id)
    return jsonify({'queue': make_public_queue(queue[0])})

# Fetches next job with QUEUED status (next job to print)
# Other job statuses are ignored
@app.route('/3dp-api/queues/<int:queue_id>/fetch', methods=['GET'])
def fetch_next_job(queue_id):
    queue = find_queue(queue_id)
    if len(queue) != 0:
        job_ids = queue[0]['jobs']
        if len(job_ids) > 0:
            for job_id in job_ids:
                job = find_job(job_id)[0]
                if job['status'] == 0: # return first 'QUEUED' status
                    return get_job(job_id)

    return jsonify({"job": None})

# Creates a new print queue
# Required parameters: Queue name
@app.route('/3dp-api/queues', methods=['POST'])
def add_queue():
    if not request.json or not 'name' in request.json:
        abort(400)

    queue = {
        'id': queues[-1]['id'] + 1 if len(queues) > 0 else 1,
        'name': request.json['name'],
        'jobs': []
    }

    queues.append(queue)
    return jsonify({'queue': make_public_queue(queue)}), 201

# Moves given job on queue to front
@app.route('/3dp-api/queues/<int:queue_id>/promote', methods=['PUT'])
def promote(queue_id):
    queue = find_queue(queue_id)

    if len(queue) == 0:
        abort(404)
    if not request.json or not 'job_id' in request.json:
        abort(400)

    job_ids = queue[0]['jobs']
    job_id = request.json['job_id']
    if job_id in job_ids:
        job_ids.remove(job_id)
        job_ids.insert(0, job_id)

    return jsonify({'queue': make_public_queue(queue[0])}), 200

# New job order (new job ids must match old job ids)
@app.route('/3dp-api/queues/<int:queue_id>/reorder_jobs', methods=['PUT'])
def reorder_jobs(queue_id):
    queue = find_queue(queue_id)
    if len(queue) == 0:
        abort(404)

    if not request.json or not 'new_order' in request.json:
        abort(400)

    job_ids = queue[0]['jobs']
    new_job_ids = request.json['new_order']
    if sorted(job_ids) == sorted(new_job_ids):
        queue[0]['jobs'] = new_job_ids

    return jsonify({'queue': make_public_queue(queue[0])}), 200


# Deletes queue with given ID
@app.route('/3dp-api/queues/<int:queue_id>', methods=['DELETE'])
def delete_queue(queue_id):
    queue = find_queue(queue_id)

    if len(queue) == 0:
        abort(404)

    # Remove queue from queue list
    queue = queue[0]
    queues.remove(queue)

    # Remove queue's jobs too
    deleted_jobs = []
    for id in queue['jobs']:
        deleted_jobs.append(find_job(id)[0])
    
    for job in deleted_jobs:
        jobs.remove(job)

    return jsonify({'result': True})



''' Jobs - methods for creating, deleting jobs '''

# Displays all jobs
@app.route('/3dp-api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({'jobs': [make_public_job(job) for job in jobs]})

# Displays info about job with given ID
@app.route('/3dp-api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = find_job(job_id)
    return jsonify({'job': make_public_job(job[0])})

# Submit new print job
# Required parameters: Job title, filename
# Optional: queue ID to assign to (assigns to first queue otherwise)
@app.route('/3dp-api/jobs', methods=['POST'])
def submit_job():
    if not request.json:
        abort(400)
    if not 'title' in request.json:
        abort(400) #TODO: change error
    if not 'filename' in request.json:
        abort(400)
    if not 'queue_id' in request.json:
        # if queue not specified, assign to first queue
        request.json['queue_id'] = queues[0]['id']

    job = {
        'id': jobs[-1]['id'] + 1 if len(jobs) > 0 else 1,
        'title': request.json['title'],
        'filename': request.json['filename'],
        'status': 0,
        'queue_id': request.json['queue_id']
    }

    jobs.append(job)

    queue = find_queue(job['queue_id'])
    # Queue must exist!
    if len(queue) == 0:
        abort(400)
    queue[0]['jobs'].append(job['id'])

    return jsonify({'job': make_public_job(job)}), 201

# Deletes print job with given ID
@app.route('/3dp-api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = find_job(job_id)
    if len(job) == 0:
        abort(404)

    # Remove job from jobs list and its queue
    job = job[0]
    jobs.remove(job)
    queue = find_queue(job['queue_id'])[0]
    queue['jobs'].remove(job_id)

    return jsonify({'result': True})

# Change job status
@app.route('/3dp-api/jobs/<int:job_id>/new_status', methods=['PUT'])
def update_job_status(job_id):
    job = find_job(job_id)
    if len(job) == 0:
        abort(404)

    if not request.json or not 'new_status' in request.json:
        abort(400)

    new_status = request.json['new_status']
    if new_status in JOB_STATUS:
        job[0]['status'] = new_status

    return jsonify({'job': make_public_job(job[0])}), 200

''' Helper functions '''

def make_public_job(job):
    new_job = {}
    for field in job:
        if field == 'id':
            new_job['uri'] = url_for('get_job', job_id=job['id'], _external=True)
        elif field == 'status':
            new_job[field] = JOB_STATUS[job[field]]
        else:
            new_job[field] = job[field]
    return new_job

def make_public_queue(queue):
    new_queue = {}
    for field in queue:
        if field == 'id':
            new_queue['uri'] = url_for('get_queue', queue_id=queue['id'], _external=True)
        elif field == 'jobs':
            job_ids = queue['jobs']
            jobs_list = []
            for id in job_ids:
                job = find_job(id)
                jobs_list.append(make_public_job(job[0]))
            new_queue[field] = jobs_list
        else:
            new_queue[field] = queue[field]
    return new_queue

def find_job(job_id):
    return filter(lambda j: j['id'] == job_id, jobs)

def find_queue(queue_id):
    return filter(lambda q: q['id'] == queue_id, queues)


''' Error handling '''

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)