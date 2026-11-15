# NASA Earthdata setup

1. Create an account at https://urs.earthdata.nasa.gov/users/new and verify your email.
2. In `/Users/karanveer/Documents/Earth_Science_Detection`, copy `.env.example` to a file named `earthdata.env` (no `.txt`). The file belongs beside `requirements.txt`, not inside `frontend` or `backend`. An existing `.env` is also supported and takes precedence when both files exist.
3. Enter your own values locally:

```dotenv
EARTHDATA_USERNAME="your_username"
EARTHDATA_PASSWORD="your_password"
```

Do not paste these values into chat or frontend files. Both `.env` and `earthdata.env` are excluded from Git. The server reads the file directly; the configuration check never returns credentials. Settings are reread on each authentication attempt, so updating the file does not require restarting the server.

`GET /api/sources/status` reports only whether both settings exist. A configured file is not proof that NASA has accepted the login or that an extraction has completed. Individual services can require first-use application authorization in Earthdata or an AppEEARS sign-in. Numerical-data integrations and validation are still required for each scientific product; creating an account alone does not implement those adapters.

Some services require first-use authorization. Sign into https://urs.earthdata.nasa.gov/, choose **Applications → Authorized Apps → Approve More Applications**, and review the application and any terms yourself. AppEEARS applies to the configured land extraction profiles; NASA GES DISC applies to atmospheric archive data when enabled. Signing into https://appeears.earthdatacloud.nasa.gov/ once also lets you inspect submitted tasks. Successful login alone does not confirm access to every archive. Public NASA GIBS map imagery and NOAA's public MUR extraction service do not require this account.

NASA documentation: https://urs.earthdata.nasa.gov/documentation/for_users/how_to_preauth_app
