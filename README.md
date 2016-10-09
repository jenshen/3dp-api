# 3dp-api

Jenny Shen (jenshen@mit.edu) | October 8 2016

Written using Python and Flask

## Running the app
First clone this repository:
```
git clone git@github.com:jenshen/3dp-api.git
```

In the root directory `/3dp-api`, make sure the last line in `app.py` is `app.run(debug=False)`. Then run `./.app.py`.

The API supports managing multiple queues. By default, there is a single print queue and no print jobs.
Queues can be added and deleted. 

#### Displaying queues and jobs

Display all queues/jobs:
```
curl http://localhost:5000/3dp-api/queues
curl http://localhost:5000/3dp-api/jobs
```
Displaying a specific queue/job
```
curl http://localhost:5000/3dp-api/queues/[queue_id]
curl http://localhost:5000/3dp-api/jobs/[job_id]
```

#### Adding and deleting print jobs
Just the print job `title` and `filename` parameters are required. Can also add `queue_id`, but if not specified the first queue is chosen. Print jobs are added with a `'QUEUED'` state.
```
curl -H "Content-Type: application/json" -X POST -d '{"title":"Bunny", "filename":"bunny.stl"}' http://localhost:5000/3dp-api/jobs
```

Deleting jobs:
```
curl -H "Content-Type: application/json" -X DELETE http://localhost:5000/3dp-api/jobs/[job_id]
```

#### Rearranging print jobs
Print jobs can be rearranged within a queue. This can be done two ways: (1) Moving a single job to the front of the queue and (2) Resubmitting a new queue order with the same jobs.

(1) Moving a single job to the front
```
curl -H "Content-Type: application/json" -X PUT -d '{"job_id":[job_id]}' http://localhost:5000/3dp-api/queues/[queue_id]/promote
```
(2) Resubmitting a new queue order

The new queue order must contain the same jobs as the old order.
```
curl -H "Content-Type: application/json" -X PUT -d '{"new_order":[list of job_id's]}' http://localhost:5000/3dp-api/queues/[queue_id]/reorder_jobs
```

#### Fetching next job to print
This will return the next `QUEUED` job. If there are no `QUEUED` jobs, no job is returned.
```
curl http://localhost:5000/3dp-api/queues/[queue_id]/fetch
```

#### Updating job statuses
The software running on a 3D printer might want to update the job status.
The job statuses are: `QUEUED`, `IN_PROGRESS`, `DONE`, `ERROR`.
```
curl -H "Content-Type: application/json" -X PUT -d '{"new_status":"new_status"}' http://localhost:5000/3dp-api/jobs/[job_id]/update_status
```

#### Adding and deleting queues
For adding queues, just the parameter `name` is required.
```
curl -H "Content-Type: application/json" -X POST -d '{"name":"another-queue"}' http://localhost:5000/3dp-api/queues
```

Deleting queues:
```
curl -H "Content-Type: application/json" -X DELETE http://localhost:5000/3dp-api/queues/[queue_id]
```
