
import re
import json
import argparse
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from google.cloud import secretmanager

def main():
    example_text = '''
    Examples:

    To dump all the secrets from <gcp_project_id> to .env file

        python3 get_all_secrets.py <gcp_project_id>


    To dump all the secrets from <gcp_project_id> filtered by label (for example with label 'env: stage')

        python3 get_all_secrets.py <gcp_project_id> --filter labels.env=stage


    To dump all the secrets from <gcp_project_id> to .env.json file

        python3 get_all_secrets.py --format json <gcp_project_id>
        
        
    To dump all the secrets from <gcp_project_id> to STDOUT

        python3 get_all_secrets.py --format stdout <gcp_project_id>


    To dump all the secrets from <gcp_project_id> to cookiemonster.env file in key/value

        python3 get_all_secrets.py --filename cookiemonster.env <gcp_project_id>


    To dump all the secrets from <gcp_project_id> to cypress.env.json file in json format

        python3 get_all_secrets.py --format json --filename cypress.env <gcp_project_id>
    '''
    parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, epilog=example_text, prog='satori_sec_pull_gcp', 
      usage='satori_sec_pull_gcp [-h] [--filter] [--format] [--filename] <gcp_project_id>'
    )
    parser.add_argument("gcp_project_id", type = str, help = "ID or name of the GCP project - required")
    parser.add_argument("--filter", type = str, help = "Filter secrets with labels", metavar = '' ,required = False)    
    parser.add_argument("--format", type = str, choices=['json', 'env', 'stdout'], help = "Output format (json / env / stdout). Default is env", metavar = '' ,required = False, default = "env")
    parser.add_argument("--filename", type = str, help = "Output filename. Default is .env or .env.json (depends on --format flag)", metavar = '' ,required = False, default = ".env")

    args = parser.parse_args()
    # Create the secret manager client
    client = secretmanager.SecretManagerServiceClient()

    gcp_project_id = args.gcp_project_id
    filter_str = args.filter
    filename = args.filename
    secrets = list_secrets_with_filter(gcp_project_id, filter_str, client)
    secrets_ver = access_secret_version(gcp_project_id, secrets, client)
    # Get all the project secrets to .env file (JSON format or key/value) or STDOUT
    if (args.format=="json"):
        secrets_to_json(secrets_ver, gcp_project_id, filename)
    elif (args.format=="env"):
        secrets_to_env(secrets_ver, gcp_project_id, filename)
    elif (args.format=="stdout"):
        secrets_to_stdout(secrets_ver, gcp_project_id)
    else:
        print("Please provide --format flag with parameter")

def list_secrets_with_filter(gcp_project_id, filter_str, client):

    # Build the resource name of the parent project
    parent = f"projects/{gcp_project_id}"
    
    secrets = {}

    # List all secrets names with filter
    if not filter_str:
        print(f"\nListing all the secrets names in project {gcp_project_id}")
    else:
        print(f"\nListing all the secrets names in project {gcp_project_id} with filter {filter_str}")
    try:
        for secret in client.list_secrets(request={"parent": parent, "filter": filter_str}):
            # print(client.list_secrets(request={"parent": parent, "filter": filter_str}))
            strValue = re.sub(".*/", '', format(secret.name))
            secrets[strValue] = None
            print(f"Found secret {strValue}")    
            # print(secrets)
        if not any(secrets):
            print(f"No secrets are found in project {gcp_project_id} with filter {filter_str}")
            sys.exit(1)
        else:
            return secrets
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

def access_secret_version(gcp_project_id, secrets, client):

    secrets_dict = {}
    secrets_list = []

    print("\nGetting all the secrets values")
    for secret in secrets.keys():
      secrets_list.append(secret)
      print(secret)
      
      # Build the resource name of the secret version.
      name = f"projects/{gcp_project_id}/secrets/{secret}/versions/latest"

      # Access the secret version
      try:
        response = client.access_secret_version(request={"name": name})
      # print(response)
      except Exception as e:
            print(f"ERROR: {str(e)}")
            sys.exit(1)

      # Store the secret payload
      secrets_dict[secret] = response.payload.data.decode("UTF-8")

    return secrets_dict

def secrets_to_stdout(secrets, gcp_project_id):

    print(f"\nDumping secrets from project {gcp_project_id} to STDOUT\n")
    try:
        for key, value in secrets.items():
            print(f"{key.upper().replace('-','_')}={value}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

def secrets_to_env(secrets, gcp_project_id, filename):

    print(f"\nDumping secrets from project {gcp_project_id} to {filename} file\n")
    file = open(filename, "w")
    try:
        for key, value in secrets.items():
            file.write(f"{key.upper().replace('-','_')}='{value}'\n")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    finally:
        file.close()

def secrets_to_json(secrets, gcp_project_id, filename):

    print(f"\nDumping secrets from project {gcp_project_id} to {filename}.json file\n")
    file = open(filename+".json", "w")
    try:
        for key in list(secrets.keys()):
            if not isinstance(key, str):
                continue
            value = secrets[key]
            del secrets[key]
            secrets[key.replace("-","_")] = value
        json.dump(secrets, file, indent=2, sort_keys=False)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    finally:
        file.close()

if __name__ == "__main__":
    main()

