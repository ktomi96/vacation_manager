# This is a vacation manager software

## Installation:

**Prerequisite: You need to have _docker_ installed**

---

To install docker image you need to run the following commands:

```bash
mkdir database
docker run -ti --pull always --network=host -v $(pwd)/database:/app/website/database ghcr.io/ktomi96/vacation_manager:latest
```

This will make a new directory, where config file and databese will be stored.
To keep using the latest version of the docker image, keep using the command to run it:

```bash
docker run -ti --pull always --network=host -v $(pwd)/database:/app/website/database ghcr.io/ktomi96/vacation_manager:latest
```

---

## Setup

First time you need to fill out the forms on the setup page

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- Allow insecure connection (http)
- sender email address
- password for the sender email account

**The _first_ user logging in, will get _admin_ privilege !**

To get your own api keys learn more at [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

### Disclamer:

for http connection you need to give: 1

by default email server is : 'smtp.gmail.com'

the config is stored in database/.env

---

## Usage

Every new user needs to get aproved by the admin. 

After they get user privilege, they can view the event calendar, request new vacation, or delete requests. By default you have 20 days of vacation, admin can change it to higher number of vacation days.

Users will get email notification if theri request has been changed.


The guest viewer can view the calendar.

Email template can be edited at /templates/email.html
