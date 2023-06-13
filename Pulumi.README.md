## General SUMARAI Infrastructure

This stack creates an AWS EC2 instance, installs a repository with dependencies and serves a streamlit app.

Therefore, we create:
- AWS EC2 Instance:
- AWS Lambdas
   - Start:
   - Stop:
- Eventbridge Rules
- Required policies
- Elastic IP

### Setup
Simply run: 

```sh
pulumi up
```

Then, update your SSH config with the following lines to be able to connect with the EC2 instance.

```yaml
Host EC2-pulumi-GPU
    HostName ${outputs.instance_public_dns}
    User ubuntu
    IdentityFile C:/Users/rbeer/.ssh/SUMARAI-EC2.pem
```

Now, you can SSH into the EC2 instance and run the following commands to watch the services:
- wait until all conda environments are completely installed (up to 10 minutes): `watch -n 1 conda env list`
    - `pdm-cc-aws-ec2`
- watch streamlit app service status: `watch -n 1 sudo systemctl status streamlit-app`
- watch fastapi service status: `watch -n 1 sudo systemctl status fastapi`
- wait until the services are online (this may take around 15 minutes when creating the instance, subsequently the services should be online in less than 5 minutes)

PS: If you want to debug, make sure to install VS Code Python Extension on EC2 instance.

## Restarting the EC2 instance

Currently, the EC2 instance will be shut down and restarted periodically automatically.

If you want to debug, you may need to start the instance.

You can do this via the AWS Console or via the AWS CLI with the following commands:

```sh
aws ec2 start-instances --instance-ids ${outputs.instance_id}
```
