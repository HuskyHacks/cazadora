# Cazadora
Simple hunting script for hunting sussy M365 OAuth Apps.

## About
This is a very quick triage script that does the following:
- Uses device code authentication to retrieve a token for a user
- Uses that token to call the Graph API to enumerate the user's tenant and collect the the tenant applications and service principals.
- Runs several hunting rules against the collected output.
- Organizes and color codes the results.

## How-to
- Clone the directory and change directories into it.
- Install the dependencies:
```
$ pip3 install -r requirements.txt
```
> (See the docker quickstart if you don't want to fuss with venv and dependencies)
- Run the script with the optional -o for the outfile:
```
$ python3 main.py [-o] [outfile.json]
```
- Follow the instructions to authenticate using device code flow. The script will handle the rest!

## Docker Quickstart
I hate Python dependencies too, so I threw in a simple Dockerfile to run the script:
```
$ docker build -t cazadora && docker run -it cazadora
```
Then, follow the instructions like normal.

## What are we looking for?
This script hunts for a small collection of observed OAuth TTPs. These TTPs come from threat intel and observing OAuth application tradecraft from researching the Huntress partner tenants at scale. This script looks for the following:

- Apps with only non-alphanumeric characters in the name (i.e.: apps named "...")
- Apps named after an identity in the tenant, especially if that identity is the assigned user for the app (i.e., an app named "lowpriv@huskyworks.onmicrosoft.com")
- Apps named "test", "test app", or something similar.
- Apps with a reply URL that matches: `http://localhost:[some_port_number]/access` with or without a trailing forward slash.
- Apps that we consider to be [Traitorware](https://huntresslabs.github.io/rogueapps/).

