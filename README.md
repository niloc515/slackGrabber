# Slack Grabber

## Purpose

To download all files off a given slack channel. 

This will be accomplished with a python script which will have to be run to fetch all the files and place them into a local directory.

## How it works 

## Initial Set Up

For this application to work, the application must have access to the oauth token. This can be created by following the guide in the important documentation set up or by following the instructions below.

Go to the [Slack API page](https://api.slack.com/) and click the 'Create an App' button. Select 'From Scratch'. On the left side bar, under 'Settings', under the 'Basic Information' section, expand the 'Add Features and Functionality' section. Make sure that 'Incoming Webhooks', 'Bots', and 'Permissions' are all selected. 

Note that each option under 'Add Features and Functionality' you select may require you to navigate back to this menu.

On the left side bar, click 'OAuth and Permissions'. Under the 'Scopes' and 'Bot Token Scopes' headers, make the sure following OAuth scopes are added. 

- channels:history
- channels:join
- channels:read
- files:read
- groups:history
- im:history
- mpim:history
- incoming-webhooks

On the same page, scroll up and copy the token under the header 'OAuth Tokens for Your Workspace'. Save this for later. 

MAY HAVE TO ADD SOMETHING ABOUT THE SLACK SIGNING SECRET

Before we leave this website, go back to 'Basic Information' then click on 'Install your app' and make sure your application is installed to the correct workspace and channel.

## Installing SlackGrabber

Once you have set up the slack bot and have your API key, you can download the slackgrabber application from the Build
Release section here on Github.

If you are using a Mac, downloading and running the .dmg file will be the easiest way to install the application. 
Open the .dmg file and drag the slackgrabber application into the applications folder on your Mac.

For other systems and those having trouble with the .dmg file, download and extract the .zip or .tar bundle. You will
find the source files that you can use to build the project for your own machine. 

To build the project yourself, follow the official build instructions from the 
[Kivy website](https://kivy.org/doc/stable/guide/packaging.html). Personally, I recommend using PyInstaller instructions
when building for MacOS.

## Important Documentation 

These are links to documents that were useful while creating this application. Read for troubleshooting.

- [Guide on setting up and using the rest API](https://tommcfarlin.com/querying-the-slack-api/)
- [Why the files were not showing up in the files object](https://stackoverflow.com/questions/65646097/why-does-slacks-files-list-endpoint-return-an-empty-files-array)
- [Python3 OAuth2 requests](https://docs.informatica.com/integration-cloud/cloud-api-manager/current-version/api-manager-guide/authentication-and-authorization/oauth-2-0-authentication-and-authorization/python-3-example--invoke-a-managed-api-with-oauth-2-0-authentica.html)
- Official Slack documentation 
  - [files.list API](https://api.slack.com/methods/files.list/test)
  - [conversations.list API](https://api.slack.com/methods/conversations.list/test)
  - [conversations.join API](https://api.slack.com/methods/conversations.join/test)
