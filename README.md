# Freesoundscapes
Small Flask based application. Text based Freesound samples search and download.
This application is still under development, it has bugs and is incomplete, any contribution is welcome.

# Description
Author: Daniele Scarano

Release: 0.1 beta

# Installation
To install the app clone the repository in your computer, create a virtual environment using virtualenv (optional, but recommended). Once you have set up the virtual environment enter the folder
## Create the Database
 Create the DB using the init_db.py script, it will create a freesoundscapes.db file into the db folder
 To inspect and modify the DB schema you can check the schema.sql file
## Configuration
 ### Freesound API Key
 In order to configure the application enter the extlib directory and copy the myToken.py.template file into myToken.py
 Edit the myToken.py and add your Freesound API key following the instruction provided into the same file.
 ### App Config
 Edit the 'config' section in the main app file to customize your app according to your needs

# Licence
 This application is released under General Public Licence V2 GPL_V2

 Copyright (c) 2016 Daniele Scarano

 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Credits

 This app uses the [Freesound API](https://www.freesound.org/docs/api/overview.html) to access the website content and it is based on the [freesound_python](https://github.com/MTG/freesound-python.git) lib developed at MTG
