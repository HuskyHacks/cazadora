# Cazadora
Simple hunting script for hunting sussy M365 OAuth Apps.

![image](https://github.com/user-attachments/assets/65e62d12-1165-4177-892e-252001bfe899)

## About
This is a very quick triage script that does the following:
- Uses [device code authentication](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code) to retrieve a token for a user.
- Uses that token to call the Graph API to enumerate the user's tenant and collect the the tenant. applications and service principals.
- Runs several hunting rules against the collected output.
- Organizes and color codes the results.

## How-to
> 💡 You will need to authenticate with a user that can run queries against the Graph API. I recommend using an administrator user from the target tenant.

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
- Go to the link in the output (https://microsoft.com/devicelogin)

![image](https://github.com/user-attachments/assets/36fa63e2-5838-465c-ba0e-6d594146a221)

- Enter the code provided by the script.

- Authenticate with a user that can call the Graph API. Enter your username, password, and complete MFA.

- The prompt will read "Are you trying to sign into Microsoft Office?" The script is using device code authentication with the Microsoft Office client ID to retrieve a token after authentication. Select "Continue"

![image](https://github.com/user-attachments/assets/9e10120a-bdd2-4b2e-abaa-6a641daa6d50)

The script will handle the rest! If it finds any suspicious apps, it will print out the application's information along with a color coding for the confidence of the finding.

![image](https://github.com/user-attachments/assets/8e8dd670-d9ae-4260-9700-83e80489b337)


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

## References
- https://huntresslabs.github.io/rogueapps/
- https://www.proofpoint.com/us/blog/cloud-security/revisiting-mact-malicious-applications-credible-cloud-tenants
- https://www.proofpoint.com/us/blog/email-and-cloud-threats/defeating-malicious-application-creation-attacks

## Disclaimer
This script cannot definitively prove that your tenant does not have any suspicious applications installed in it. The absence of evidence is never the evidence of absense. Please do your own due diligence during investigation, whether this script identifies potentially suspicious apps or not.

This script is distributed with a hope that it will be useful, but myself nor Huntress are promising its efficacy. Please see the LICENSE file for more info.
