# Cazadora
Simple hunting script for hunting sussy M365 OAuth Apps.

![image](https://github.com/user-attachments/assets/65e62d12-1165-4177-892e-252001bfe899)

## About
This is a very quick triage script that does the following:
- Uses [device code authentication](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code) or the Azure SDK web login module to retrieve a token for a user that is scoped to perform Graph API calls.
- Uses that token to call the Graph API to enumerate the user's tenant and collect the the tenant's applications and service principals.
- Runs several hunting rules against the collected output.
- Organizes and color codes the results.

## How-to
> 💡 You will need to authenticate with a user that can run queries against the Graph API. I have not tested the script outside of my own testbed tenant and can't guarantee it works everywhere.

- Clone the directory and change directories into it.
- Install the dependencies:
```
$ pip3 install -r requirements.txt
```
> (See the docker quickstart if you don't want to fuss with venv and dependencies)

- Run the script with your desired authentication type (supports device code authentication by default and web browser interactive login with the Azure SDK). You can also specify `--output` for the outfile 

```
$ python3 main.py --auth-mode [device_code, azure_sdk] [--output] [outfile.json]
```
### Device Code Auth
- If using device code, go to the link in the output (https://microsoft.com/devicelogin)

![image](https://github.com/user-attachments/assets/36fa63e2-5838-465c-ba0e-6d594146a221)

- Enter the code provided by the script.

- Authenticate with a user that can call the Graph API. Enter your username, password, and complete MFA.

- The prompt will read "Are you trying to sign into Microsoft Office?" The script is using device code authentication with the Microsoft Office client ID to retrieve a token after authentication. Select "Continue"

![image](https://github.com/user-attachments/assets/9e10120a-bdd2-4b2e-abaa-6a641daa6d50)

> ⚠ I find it necessary to remind people:
> **NEVER, EVER, EVER EVER EVER** enter a device code from an untrusted source. If you receive one unprompted from an email and it says to go to the legit Microsoft page and enter it, DO NOT ENTER IT.
>  
> In this case, we are generating the code and retrieving it in-band by using the script, so we're good 👍

The script will handle the rest! If it finds any suspicious apps, it will print out the application's information along with a color coding for the confidence of the finding.

![image](https://github.com/user-attachments/assets/8e8dd670-d9ae-4260-9700-83e80489b337)

### Azure SDK Web Browser Login
> This is tricky to use with things like containers and WSL, so I'd recommend using device code auth if you're in that position

- If using the web browser auth, the browser will open to the Microsoft login portal. Sign in with your username, password, and MFA.
- The script will handle the rest!

## Docker Quickstart
I hate Python dependencies too, so I threw in a simple Dockerfile to run the script:
```
$ docker build -t cazadora . && docker run -it cazadora
```
Then, follow the instructions like normal. This likely won't work well if you're using the interactive web portal login option but it works just fine with device code auth.

## What are we looking for?
This script hunts for a small collection of observed OAuth TTPs. These TTPs come from threat intel and observing OAuth application tradecraft from researching the Huntress partner tenants at scale. This script looks for the following:

- Apps with only non-alphanumeric characters in the name (i.e.: apps named "...")
- Apps named after an identity in the tenant, especially if that identity is the assigned user for the app (i.e., an app named "lowpriv@huskyworks.onmicrosoft.com")
- Apps named "test", "test app", or something similar.
- Apps with a reply URL that matches: `http://localhost:[some_port_number]/access` with or without a trailing forward slash.
- Apps that we consider to be [Traitorware](https://huntresslabs.github.io/rogueapps/).

## Mitigation
So if you're thinking "hey, hunting these apps is great, but what's the best way to prevent them from showing up at all?" then I like the cut of your jib.

By default, any identity in a tenant can install any app without requiring permission. Subsequently, that user can consent to any permissions that affect their own resources. So while many heavy hitting permissions (mostly the ".All" permissions) require admin consent, your average user can and will happily hand over consent to permissions to access their own emails, contacts, and the like unless you disable that default config.

I'd recommend reading about [configuring how users consent to applications](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent?pivots=portal). I'd also recommend looking at [Merill Fernando's resource on Graph API permissions](https://graphpermissions.merill.net/permission/) to get an idea of any given application's permission power, which ones can be installed without admin consent, and which ones require admin consent. Keep in mind that the Graph API is just one of the many resources an app can have permissions over. 


## References
- https://huntresslabs.github.io/rogueapps/
- https://www.proofpoint.com/us/blog/cloud-security/revisiting-mact-malicious-applications-credible-cloud-tenants
- https://www.proofpoint.com/us/blog/email-and-cloud-threats/defeating-malicious-application-creation-attacks

## Disclaimer
This script cannot definitively prove that your tenant does not have any suspicious applications installed in it. The absence of evidence is never the evidence of absense. Please do your own due diligence during investigation, whether this script identifies potentially suspicious apps or not.

This script is distributed with a hope that it will be useful, but we (myself and Huntress) do not make any promises or guarantees about its efficacy. Please see the LICENSE file for more info.
