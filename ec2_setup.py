# TODO: recreate prefect api key and add it here implicitly (or use a secret)

# Create a startup script
general_setup = """#!/bin/bash
sudo yum update -y
conda init bash
conda update -n base conda
# conda config --set report_errors false
conda install -c conda-forge micromamba -y
pip install --upgrade pip
"""

# Create a bash script that returns the git token
git_setup = """
cat > /home/ubuntu/git_askpass.sh << 'EOL'
#!/bin/sh
echo "$GIT_TOKEN"
EOL
chmod +x /home/ubuntu/git_askpass.sh
"""

# Clone the private Git repository
git_clone_repository ="""
cat > /home/ubuntu/git_clone_repository.sh << EOL
#!/bin/bash
export GIT_ASKPASS="./git_askpass.sh"
# export GIT_TOKEN=
git clone https://github.com/pybites/fastapi_demo.git /home/ubuntu/code/fastapi_demo
sudo chmod 777 /home/ubuntu/code -R
EOL
chmod +x /home/ubuntu/git_clone_repository.sh

/home/ubuntu/git_clone_repository.sh
"""
# TODO: add the git clone command here

create_setup_script_fastapi = """
cat > /home/ubuntu/setup_fastapi.sh << 'EOL'
#!/bin/bash
# install dependencies
conda create -n fastapi python=3.9 -y
source activate fastapi
pip install -r /home/ubuntu/code/fastapi_demo/requirements.txt

EOL

chmod +x /home/ubuntu/setup_fastapi.sh
"""
# TODO: create env.yml and update paths here

create_run_script_fastapi = """
cat > /home/ubuntu/run_fastapi.sh << 'EOL'
#!/bin/bash
cd /home/ubuntu/code/fastapi_demo
source activate fastapi
uvicorn app:app --reload --host 0.0.0.0 --port 80
EOL

chmod +x /home/ubuntu/run_fastapi.sh
"""

create_service_script_fastapi = """
cat > /etc/systemd/system/fastapi.service << EOL
#!/bin/bash

[Unit]
Description=FastAPI
After=network.target

[Service]
User=ubuntu
EnvironmentFile=/home/ubuntu/.bashrc
ExecStart=/home/ubuntu/run_fastapi.sh
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL
"""

# TODO: create streamlit setup, run and service script

# Execute commands
execute_commands = """#!/bin/bash

/home/ubuntu/setup_fastapi.sh
sudo systemctl enable fastapi.service
sudo systemctl start fastapi.service
"""


user_data = ( 
            general_setup + git_setup +
            git_clone_repository + 
            create_setup_script_fastapi +
            create_run_script_fastapi + 
            create_service_script_fastapi +
            execute_commands
            )

# check prefect agent service status with: 
