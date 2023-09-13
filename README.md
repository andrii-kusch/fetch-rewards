
# Fetch Rewards

# Data Engineering Take Home: ETL off a SQS Queue

  

This is a python implementation of an ETL pipeline. The pipeline reads messages from AWS sqs queue, the messages have Json format and contain user login information. The pipeline masks specific fields containing personal identifiable information and writes the masked data to Postgres DB.

  

The solution is broken down into three modules: extraction, transformation and load, with corresponding unit test cases. The project is designed to be as simplistic and minimalistic as possible, yet to encompass (or at least mimic) all important components a similar real-life, production-size solution would have.

  

The work presented here was accomplished in a about 4 - 4.5 hours with all the coding (~2 h), testing (~1h) and documentation (~1h, maybe the last part is harder for me as I am not a native speaker of English). Personally, I think a timeline of two hours to complete this assignment and make it submission ready is not realistic.

  

However, I enjoyed this a lot! Thank you so much for great experience, guys, and let's dive into it!

  

## Running the pipeline

For local deployment use Docker Compose:

```

docker-compose up

```

Docker Compose will spin up localstack and postgres containers, build image for etl service, run unittests, and deploy a set number of the etl service replicas.

  

## Configuration

There are several parameters that can be configured to change etl service's behavior, demontrate replication, concurency and simulate different real-life scenarios. These parameters can be set in docker-compose.yaml, mostly as environment variables. For some of them, if not scecifeid, default values will be used, others have to be set.

  

1) replicas. Specifies how many instances of ets service will be deployed and process messages from AWS sqs in parallel. This parameter must be specified.

2) max_messages. Sets how many messages at most can be received at once. By default is set to 10, which is the maximum AWS sqs queue can receive at once.

3) keep_listening. Describes behaviour after the sqs queue appers to be empty. If set to true (or 1, or yes) will keep etl containers running and periodically check if new messages appear in the queue. If set, after the queue is exhausted, elt service will switch to long pooling, checking the state of the queue only so often.

4) long_pooling. For how long (in secs) sqs queue will be waiting for new messages after switching to long pooling.

5) writting_buffer_size. A number of messages that, once reached, will be commited to Posgres in a single transaction.

  

In addition to above, you can specify default AWS credentials, region and logging level.

  

## Debugging

Python code of this project can be ran and interactively debugged in an IDE of you choice. For that make sure that:

1) Localstack and Postgres containers are running;

2) endpoint (main.py, line 10) and host (postgres.py, line 14) are set to "localhost" as your debugger is outside of Docker and from its perspective everything is happening on your local machine. For containerized execution these values should be set to localstack and postgres correspondingly, as described in comments, as from Docker's perspective, containers are separate "machines" connected by Docker's (default) network.

  

## Testing

Even though Docker Compose executes unittest test cases during deployment, you may choose to run them manually. For that run

```

python -m unittest discover -v test

```

from project root

  

## Design desicions and assumptions

Let us talk about decisions and assumptions that were made to implement this solution in just few hours that were given.

  

### Replication

The solution was implemented with an idea of concurrency and scalability in mind. You can run only one instance of the etl service, but it was designed to be replicated.

  

### Batching

The solution is designed to process configurable batches of messages, both for reading and writing. These parameters (see above) allow to optimize performance and mitigate stress experianced by Postgres.

  

### Python generators

When reading messages from the queue, we yield results using python generators (lazy iterators). It is an excellent mechanism to achieve good performance and use RAM conservatively. In my opinion, in (Python powered)data engineering generators should be used wherever possible.

  

### Data validity

We cannot assume correctness of input. We do our best to process inputs as fast as we can, if an error occurs that prevents message from being recorded, the error is logged and the message is ignored.

  

### Masking of PII

We use SHA256 to hash values also using user_id as salt. It's simple, but gets work done. Hash is salted this way for two reasons: 1) It makes it harder to reverse masking using rainbow tables (for IPs it would be trivial, IP v4 that is); 2) People may share physical device but use different accounts. For that reason we do not consider different users connecting from the same IP with the same device ID duplicates of each other. Speaking of duplicates though...

  

### Deduplication

We do not know I cannot reliably know if records in the queue contain duplicates, so we are forced to assume that they do not. Records do not really have any field that would allow reliable deduplication, for login information that would be something like session_id or at least a timestamp and a duration of login, if we use user_id. However we only add date ourselves and a user can login more than once a day. For that reason we are also forced to use INSERT into Postgres, if we had a reliable deduplication field like session_id, we could use UPSERT instead.

  

### ETL service load balancing

Processing of our records is blazing fast and we have very few of them, which likely would not be the case in real life. In fact, it is so fast that if you spin up more than one etl container, often times just one of them will take all the work, leaving nothing to other(s). I added a sleep statement in transform() method to simulate work taking more time. This allows to really show how work can be evenly distributed among multiple containers.

  

### Strategy to write to Postgres

There is only one instance of Postgres in this solution, so the rest of it should adjust and accommodate this limitation. Instances of elt service create connection and cursor once and reuse them to commit multiple records in one transaction. This does not matter on the scale of this example but it would if we had to process millions of records.

  

### Requirements.txt

Requirements.txt are minimal and and precise. Versions are specified exactly to guarantee identical behaviour. (Leraned the hard way with modules like pyarrow and boto3).

  

## Next steps and future work

Now let us imagine what could happen if this project grew in size and complexity into a full-size production implementation.

  

### Thoughtful design

This solution is split into three modules to reflect that it is dowing ETL (one module for each letter). It also does not use OOD (testcases don't count). A real life soluton would likely have a much more complex OOP design involving abstraction, inheritance, composition, delegation and whatnot. The objects would likely interact according to some design pattern (for example, pipeline design pattern). For maintainability of the code it would be important to promote reusability of parts.

  

### CI/CD

In this example we test, build and deploy all in docker-compose. In real life there would be a dedicated CI/CD process for that, for example Jenkins, Azure, Spinnaker.

  

### More testing

Every project could use more testing. Vigorous regression, unit and integration testing can save many hours of work and a lot of money.

  

### Automated scalability

In the provided code we can choose (hardcode) how many replicas we want or if we want for containers to keep listening for messages after the queue is exausted. In real life we could have an automated process that spins up and shuts down replicas dynamically to accomodate changing demand. Parameters like batch size and long pooling wait can also be changing dynamically to inteligently balance perfomance and maintanance cost.

  

### Container orchestration

Depending on how numerous and complex our containers may become, we may need a dedicated container orchestration service like Kubernetes or AWS Fargate.

  

### Logging and monitoring

Tools like Datadog or Grafana can be used for application health monitoring, dashboarding and alerting.

  

### Postgres

Our database storage service can be scaled up too! Using indexing, replication and sharding we can make our database ready for extremely high loads.

  

## Last thoughts

I am likely forgetting other important things. Please let me know if you have any questions! And hope to discuss this with you soon