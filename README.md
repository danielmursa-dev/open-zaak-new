# open-zaak-new

This repository is dedicated to identifying potential performance bottlenecks in **OpenZaak**.

The main goal is to rebuild OpenZaak from scratch, **adding one feature at a time**, and monitoring the performance impact at each step.

After every changes, performance tests are executed using **Locust** to compare results and detect issues.

```python
locustfile = tests/test_locust.py 
headless = true
users = 20
spawn-rate = 1
run-time = 1m
```

## 📍 Notes

- All tests were conducted **locally**, so the data collected are **relative**, and must be performed on the Kubernetes cluster.
- Despite being local, the results help to understand when and how specific changes impact performance.
- Each modification has been documented in detail in an **Excel FILE**, including:
  - The feature added
  - Metrics 
  - Additional notes or observations

- The changes were also tested using a **local database**, which was created and destroyed for almost every test run.
    - To insert the test records (always tested with **1M records**), a `queries.sql` file is included in this repo. It contains the raw SQL statements executed directly on the database.
    **NOTE** Simply comment or remove the unnecessary fields from the `INSERT` statements depending on the specific TAG.

- By default, the application starts using **DRF’s base `ViewSet` and `Serializer`** classes. However, following **Sergei’s** suggestion, I also ran tests on his minimal application that doesn’t use any serializers at all. Effectively considered a **baseline (level 0)**.
    - That test application is available here: [https://github.com/sergei-maertens/gotta-go-fast](https://github.com/sergei-maertens/gotta-go-fast)
    - The `queries.sql` file also includes the raw queries used for that setup.


## 📊 Findings and Analysis: 

#### 1. Pagination and COUNT(*)

When run queries with 1M+ records using `LIMIT` and `OFFSET`, the performances are fast.  
However, the problem starts with paginated APIs, where in addition to the `LIMIT`, Django (and DRF) performs an expensive `SELECT COUNT(*)` on the full dataset. This drastically slows down response times.

- Possible solutions

One area explored is **tuning PostgreSQL configuration** to enable better parallel execution of queries. In this way the database perform more operations concurrently, especially for large table scans or aggregations.

The following custom settings were tested by modifying the PostgreSQL config file:  
`/etc/postgresql/17/main/postgresql.conf`

Custom PostgreSQL example

```conf
max_worker_processes = 32
max_parallel_workers = 32
max_parallel_workers_per_gather = 16
max_parallel_maintenance_workers = 16

work_mem = '64MB'
maintenance_work_mem = '512MB'
shared_buffers = '4GB'
effective_cache_size = '12GB'

parallel_setup_cost = 10
parallel_tuple_cost = 0.01

min_parallel_table_scan_size = '64kB'
```

links: 

https://www.rockdata.net/tutorial/postgres-optimization/
https://www.rockdata.net/tutorial/tune-parallel-query/#number-of-worker-processes

- Alternative Option: Using PostgreSQL Estimates for COUNT Queries

Another option being explored is to **improve the performance of `COUNT(*)` queries** by using **PostgreSQL's internal planner estimates** instead of executing a full row count.

This can be done by defining a custom function that extracts the estimated row count from the execution plan:

```sql
CREATE OR REPLACE FUNCTION count_estimate(
    query text
) RETURNS integer LANGUAGE plpgsql AS $$
DECLARE
    plan jsonb;
BEGIN
    EXECUTE 'EXPLAIN (FORMAT JSON) ' || query INTO plan;
    RETURN plan->0->'Plan'->'Plan Rows';
END;
$$;

-- then use it like
SELECT count_estimate('SELECT id FROM zaken_zaak');
```
- Much faster than a regular `SELECT COUNT(*)` on large tables.
- Can be triggered after running `ANALYZE`, which updates PostgreSQL’s internal statistics.

but 

- Works well **only when no `WHERE` clause is used**
 
Therefore, it is necessary to further investigate the issue related to **COUNT(*)**, because if filters are applied, the speed of this query also increases, which has not been tested so far. This scenario should be further verified.

#### 2. URL Version Resolution

There is measurable overhead in how URLs are resolved, especially when generating versioned URLs using `reverse()` with parameters like the version and the object UUID.  
By **setting the version statically**  there is slight performance improvement.

#### 3. DateTime Serialization with Timezone Handling

Date/time fields cause slowness due to **time zone conversions** performed during serialization.
A possible solution is to use `.annotate()` in queryset and return raw datetime values directly from the database, avoiding object processing.



#### 4. camelCase Library Overhead

Adding the `camelcase` conversion library introduces an average delay of **~20ms** per request.



#### 5. Geometry Field Overhead (Even When NULL)

Even though the `GEOMETRY` field was always set to `NULL` and never serialized, just changing the database backend from `django.db.backends.postgresql` to `django.contrib.gis.db.backends.postgis` introduced noticeable performance slow. 



#### 6. Optimizing Relations with `prefetch_related`

Using `prefetch_related` improves performance, but it’s even better to **limit selected fields** via `only()`
Example:

```python
Prefetch("hoofdzaak", queryset=Zaak.objects.only("uuid", "pk"))
```