Documentation
=============
ContentQ CMS is an open source managemen system to deploy a site on Google cloud.

Jose Maria Zambrana Arze <contact@josezambrana.com>

Documentation
-------------

### Windows Installation
Instructions to deploy ContentQ on google app engine in a windows machine.

####Requeriments

  - Python 2.5
  - ContentQ CMS
  - A google account


#### Step 1: Install Python
Download and install python 2.5 for windows.  
<http://www.python.org/ftp/python/2.5/python-2.5.msi>

#### Step 2: Create a google app engine app.
1. Sign in <http://appengine.appspot.com> with your google account.
2. Click on **create application** button.
3. If it is not your first application go to 6.
4. Verify your account by sms. enter your country, carrier (if needed) and your mobile phone number. Click **Send**.
5. Once you get the code on your mobile. enter it on the form. Click on Send.
6. Type your an identifier and a title for your application and click on **Create Application**
7. An application is now created. You can deploy your contentq instance.

#### Step 3 - Get ContentQ CMS
Download ContentQ source code from github:

**Github URL** <https://github.com/josezambrana/ContentQ-CMS/tree/master>  
**Github Download URL** <https://github.com/josezambrana/ContentQ-CMS/tarball/master>  
**Public Clone URL** git://github.com/josezambrana/ContentQ-CMS.git  

Extract the ZIP archive and save to a folder (c:/)

#### Step 4 - Deploying your ContentQ app
1. Open explorer and go to c:/contentq-latest/
2. Open app.yaml with some editor (Ex. notepad++) and change the value of "aplication" to your Application Identifier.
3. Open settings.py with some editor (Ex. notepad++) and change the value of "APP_ID" to your Application Identifier.
4. Open the command line.
5. Go to the project path. *cd /contentq-latest*
6. Run the command: *python manage update*
7. Enter your google username and password.
8. The site now can be configurated

#### Step 5 - Configurating your site.
1. Wait some time until the indexes start serving. You can review the status of them on your **App Dashboard>>Datastore Indexes**
2. Open a browser and go to your application address.
3. Fill the install form with the configuration for your site and the info for your admin user. Click on **install**.
4. Your contentq app is ready and you can start creating some content