# 3dp-api

NVBOTS Programming Exercise | Jenny Shen (jenshen@mit.edu) | October 8 2016

## Running the app
First clone this repository:
```
git clone git@github.com:jenshen/3dp-api.git
```

In the root directory `/3dp-api`, make sure the last line in `app.py` is `app.run(debug=False)`. Then run `./.app.py`.

The API supports managing multiple queues. By default, there is a single print queue and no print jobs.
Queues can be added and deleted. 

#### Displaying queues and jobs

Display all queues:
```
curl http://localhost:5000/3dp-api/queues # Display all queues
curl http://localhost:5000/3dp-api/jobs # Display all jobs

```

#### Adding print jobs

#### Deleting print jobs

#### Rearranging print jobs
Print jobs can be rearranged within a queue. This can be done two ways: (1) Moving a single job to the front of the queue and (2) Resubmitting a new queue order with the same jobs.

Moving a single job to the front:

Resubmitting a new queue order:

#### Adding queues
#### Deleting queues

```
```
```
```
```
```
```
```
```
```