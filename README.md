# FortifySSC
Some public domain scripts to help maintain an SSC

## Runs from Windows command line


Define the following OS variables
```
FORTIFY_HOST = Assumes https connection so just the URL like myfortify.mycompany.com; the ssc is implied.
SQLPASS = password for your SQL Fortify user
FORTIFY_TOKEN = a UnifiedLoginToken for a user with SSC admin
prod = IP / friendly name of your SQLServer DB host
prodUser = the user

NOTE FTY is the implied DB. Add another variable if you have a different name.
```

Then 
```
repeat_command1.bat
```
