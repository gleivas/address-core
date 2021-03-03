[![Build Status](https://travis-ci.com/gleivas/address-core.svg?token=EM4s1WqR5gqsAUmT7awt&branch=main)](https://travis-ci.com/gleivas/address-core)
# address-core
The project consist in an endpoint that receives part of an address and using the
[PreciselyApi](https://developer.precisely.com/) suggests possible matches.  
The technologies used:
- Python
- Terraform
- Aws Lambda
- Aws ApiGateway

# Local Setup 
Install OS dependencies:  
`apt-get install -y git make gcc curl unzip zip`  

If you have [PyEnv](https://github.com/pyenv/pyenv) installed, you can create your virtual environment and 
install the python dev dependencies:   
`make create-venv`  

Or if you wish is possible to install only the python dependencies:  
`make setup-dev`  

In order to deploy, is necessary to install [Terraform](https://www.terraform.io/) in version 0.12.29:
```
curl https://releases.hashicorp.com/terraform/0.12.29/terraform_0.12.29_linux_amd64.zip --output terraform.zip  
unzip terraform.zip  
sudo mv terraform /usr/local/bin
```

# Tests
To run your tests:  
`make test`  

To run the style guide checker:  
`make code-convention`

# Infrastructure
The infrastructure was created with Terraform, to deploy the application you need to do the following commands:  
to initialize:   
`terraform init`  

to create a new workspace:  
`terraform workspace new dev`  

or if you already have the workspace created you can select it:  
`terraform workspace select dev`  

Finally, to deploy:   
`terraform apply`  

You can also run an infrastructure test:  
`terraform plan`

# Call the API
In the root of the project there is a script to call the api,
in order to use it you need to first export your api key:  
`export api_key=YOUR_API_KEY_VALUE`  

Then you can run it:  
`python call_api.py` 

By default, it will search the addresses that matches the string "6636 AVENUE J"
if you wish to search for other address you can call it with the --search-text parameter:  
`python call_api.py --search_text "1618 Park"`