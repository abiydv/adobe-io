# Adobe I/O Cloud Manager Integration

Test 
Deploy this API Gateway + Lambda in your AWS account to get notified of executions on Adobe Cloudmanager. Notifications will be sent to both email, and MS Teams.

This can be extended to implement more functionalities like auto-approve, auto-reject pending executions etc.

Deploying this stack will create a new api endpoint, which needs to be added to the Adobe I/O console to complete the setup.

More details - https://abiydv.github.io/posts/adobe-io-cloudmanager-api

### **PREREQUISITES**
1. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) (preferably v2)
1. [Serverless framework](https://www.serverless.com/framework/docs/providers/aws/guide/installation/) 
1. Adobe I/O Cloudmanager project
1. MS Teams incoming webhook
1. AWS Account with - 
    * Custom domain on Route 53 and ACM cert for the domain
    * SES configured to send emails
    * S3 bucket to use
    * Adobe I/O keys saved in SSM

### **SETUP**

1. Create and activate virtual environment
    ```
    $ python -m venv env
    $ source env/bin/activate
    ```

1. Install dependencies
    ```
    (env) $ pip install -r requirements.txt
    ```

1. Format, lint, run tests, check coverage reports etc.
    ```
    (env) $ black src/*.py
    (env) $ flake8
    (env) $ pytest
    (env) $ coverage run -m pytest
    (env) $ coverage html
    ```

### **DEPLOY**

1. Export the credentials as environment variables. Either the access/secret keys or the aws cli profile

1. Deploy/Update the service to AWS 
    ```
    sls deploy
    ```
1. Configure the new domain endpoint (`https://example.com/adobe`) after deployment in the Adobe I/O console.

1. Adobe I/O will trigger a test request and if it returns `200`, the status of the webhook will be changed to `ACTIVE`

### **CLEANUP**

1. Remove the service
    ```
    sls remove
    ```
