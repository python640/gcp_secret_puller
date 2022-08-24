Run this script in order to fetch all the secrets from the specified GCP project secret manager and store it in .env file in key/value format or in json file in json format.
There is an option to filter secrets by labels for example.

Prerequisites:

1. Your project should have secret manager API enabled
2. You should be logged in to GCP project 
3. You should have sufficient permissions to read secrets in GCP secrets manager in this project

For some details please refer to following links:
 
https://cloud.google.com/secret-manager/docs/reference/libraries#client-libraries-install-python
https://cloud.google.com/python/docs/reference/secretmanager/latest
https://cloud.google.com/secret-manager/docs/samples
https://cloud.google.com/secret-manager/docs/filtering#examples

Install requirements:
```
pip install -r requirements.txt
```

How to run:
```
python3 get_all_secrets.py [-h] [--format] [--filename] <gcp_project_id>

positional arguments:
  gcp_project_id  ID or name of the GCP project - required

optional arguments:
  -h, --help      show this help message and exit
  --filter        Filter secrets with labels
  --format        Output file format (json / .env). Default is .env
  --filename      Output filename. Default is .env or .env.json (depends on --format flag)

Examples:

To dump all the secrets from <gcp_project_id> to .env file

    python3 get_all_secrets.py <gcp_project_id>
  
To dump all the secrets from <gcp_project_id> filtered by label (for example with label 'env: stage')

    python3 get_all_secrets.py <gcp_project_id> --filter labels.env=stage

To dump all the secrets from <gcp_project_id> to .env.json file

    python3 get_all_secrets.py --format json <gcp_project_id>

To dump all the secrets from <gcp_project_id> to cookiemonster.env file in key/value

    python3 get_all_secrets.py --filename cookiemonster.env <gcp_project_id>

To dump all the secrets from <gcp_project_id> to cypress.env.json file in json format

    python3 get_all_secrets.py --format json --filename cypress.env <gcp_project_id>
```
