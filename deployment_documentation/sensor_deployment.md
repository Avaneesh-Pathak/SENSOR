
# Sensor Fault Detection Project Deployment

To deploy our project to Aws Ec2 we have some steps which are following:

- Create DockerFile and test by building docker image locally.
- Create Github Actions YAML config file
- Set up github repository secrets 
- Create an AWS EC2 ubuntu machine 
- Install docker and AWS cli in ec2 machine
- Set up self-hosted runner in EC2 
- Create an ECR repository in aws 



 
# ![Docker](https://skillicons.dev/icons?i=docker) Create DockerFile and test by building docker image locally.

- Let's check our DockerFile that we've created for our project.
```docker
FROM python:3.8-slim-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD [ "python3","app.py" ]

```
So our base image is `python:3.8-slim-buster` and our work directory is `app.py` as this is the module where our FastApi app code is written. We are installing the requirements from the requirements.txt and atlast we are giving a command to run the app. That's all about the dockerfile that we have created for this particular project.

## Create Github Actions YAML config file

### Continuous Integration and Continuous Deployment Workflow

```YAMl

name: workflow

on:
  push:
    branches:
      - main
    paths-ignore:
      - 'README.md'

permissions:
  id-token: write
  contents: read

jobs:
  integration:
    name: Continuous Integration
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Lint code
        run: echo "Linting repository"

      - name: Run unit tests
        run: echo "Running unit tests"

  build-and-push-ecr-image:
    name: Continuous Delivery
    needs: integration
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Install Utilities
        run: |
          sudo apt-get update
          sudo apt-get install -y jq unzip
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_DEFAULT_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          IMAGE_TAG: latest
        run: |
          # Build a docker container and
          # push it to ECR so that it can
          # be deployed to ECS.
          docker build -t ${{ secrets.AWS_ECR_REPO_URI }}:$IMAGE_TAG .
          docker push ${{ secrets.AWS_ECR_REPO_URI }}:$IMAGE_TAG
          
          
  Continuous-Deployment:
    needs: build-and-push-ecr-image
    runs-on: self-hosted
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_DEFAULT_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      
      - name: Pull latest images
        run: |
         docker pull ${{ secrets.AWS_ECR_REPO_URI }}:latest
         
                
      # - name: Stop and remove visibility container if running
      #   run: |
      #    docker ps -q --filter "name=visibility" | grep -q . && docker stop visibility && docker rm -fv visibility
      - name: Run Docker Image to serve users
        run: |
         docker run -d -p 8080:8080 --name=sensor -e 'MONGO_DB_URL=${{ secrets.MONGO_DB_URL }}' -e 'AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}' -e 'AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}' -e 'AWS_DEFAULT_REGION=${{ secrets.AWS_DEFAULT_REGION }}' ${{ secrets.AWS_ECR_REPO_URI }}:latest

      - name: Clean previous images and containers
        run: |
         docker system prune -f

```
This is a GitHub Actions workflow written in YAML for continuous integration (CI) and continuous deployment (CD) of a software project.

The workflow is triggered by a push to the main branch, and it consists of three jobs:

**The integration** job runs on an Ubuntu virtual machine and checks out the code from the repository. It then runs a linter on the code and executes unit tests.

**The build-and-push-ecr-image** job also runs on an Ubuntu virtual machine and depends on the integration job. It installs some utilities and configures AWS credentials to access Amazon Elastic Container Registry (ECR). It then logs in to ECR and builds a Docker image of the project using the latest tag. Finally, it pushes the image to ECR.

**The Continuous-Deployment** job runs on a self-hosted machine and depends on the build-and-push-ecr-image job. It checks out the code from the repository and configures AWS credentials to access ECR. It then pulls the latest Docker image from ECR and runs it as a container on the machine, passing some environment variables to it. Finally, it cleans up any previous images and containers.

To use this workflow, you can copy the YAML code to a .yml file in your repository's .github/workflows directory. You also need to configure some secrets in your repository settings to authenticate with AWS and ECR.

For more information on using GitHub Actions, refer to the [official documentation](https://docs.github.com/en/actions).


## ![github](https://skillicons.dev/icons?i=github) Set up github repository secrets 

### Adding Secrets in GitHub 

    1. Navigate to the repository where you want to add the secrets.
    2. Click on the "Settings" tab in the menu bar.
    3. Scroll down to the "Secrets" section and click on "New repository secret".
    4. Enter the name of the secret and its value.
    5. Click on "Add secret" to save the secret.
    6. To use the secret in your workflow, reference it using the syntax `secrets.<secret-name>`.


### Setting Up Secrets for this project

To use the GitHub Actions workflow in this repository, you need to set up several secrets in your GitHub repository. Here's how to set up the required secrets:

- `AWS_ACCESS_KEY_ID`: The access key for your AWS account.
  - To create an access key, go to your AWS Management Console and navigate to the "IAM" service.
  - Click on "Users" in the left-hand navigation menu, then click on your user.
  - Click on the "Security credentials" tab, then click on "Create access key".
  - Copy the access key ID and store it as a secret in your GitHub repository.
- `AWS_SECRET_ACCESS_KEY`: The secret access key for your AWS account.
  - To create a secret access key, follow the same steps as for the access key, but click on "Show" to reveal the secret access key.
  - Copy the secret access key and store it as a secret in your GitHub repository.
- `AWS_DEFAULT_REGION`: The default region for your AWS account.
  - This is typically set to the region closest to you.
  - You can find the region code in the AWS Management Console, in the upper-right corner of the page.
  - Store the region code as a secret in your GitHub repository.
- `AWS_ECR_REPO_URI`: The URI for your Amazon Elastic Container Registry (ECR) repository.
  - To get the URI, go to your AWS Management Console and navigate to the "ECR" service.
  - Click on your repository, then click on "View push commands" in the upper-right corner of the page.
  - Copy the "docker login" command and extract the repository URI from it.
  - Store the URI as a secret in your GitHub repository.
- `MONGO_DB_URL`: The URL for your MongoDB database.
  - This should be a connection string in the format `mongodb+srv://<username>:<password>@<cluster>/<database>`.
  - Store the URL as a secret in your GitHub repository.



## Create an AWS EC2 ubuntu machine


## Prerequisites

Before you begin, you'll need:

- An AWS account
- The AWS CLI installed on your local machine
- Docker installed on your local machine

## Creating an EC2 Instance

1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).

2. Navigate to the EC2 dashboard.

3. Click on the "Launch Instance" button.

4. Choose an Amazon Machine Image (AMI) and instance type. For example, you have to choose the Ubuntu 22.04 AMI and t2.medium instance type for this project.

5. Configure the instance details, such as the number of instances, network settings, and storage.

6. Add any additional storage or tags, if necessary.

7. Configure the security group to allow incoming traffic. For example, you could allow HTTP and HTTPS traffic.

8. Launch the instance and save the private key for SSH access.

## Installing Docker

1. SSH into the EC2 instance using the private key.

2. Update the package index and install the required dependencies:

```bash
sudo yum update -y
sudo yum install -y docker
```

3. Start the Docker service and enable it to start on boot:
```bash
sudo service docker start
sudo chkconfig docker on
```


## Installing AWS CLI

1. SSH into the EC2 instance using the private key.

2. Download and install the AWS CLI:

```bash
sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
```

3. Verify the installation by running the following command:
```bash
aws --version
```


You're now ready to use the EC2 instance with Docker and AWS CLI.



