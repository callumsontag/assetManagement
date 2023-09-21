# Mettle Asset Management System

## Table of Contents

- [Project Name](#project-name)
- [Table of Contents](#table-of-contents)
- [Description](#description)
- [Features](#features)
- [Working Example](#working-example)
- [Installation](#installation)

## Description

An application created by myself for a level 5 degree apprenticeship module 'Software Engineering and Agile'. The idea of the application is to allow Mettle to manage IT assets owned by the company that are being used by employees of the business. This allows the company to keep track of valuable IT assets but carries the ethos of the business which is to give responsibility to each employee. This can also help in scenarios wherby certain devices may be needed to test certain aspects of other Mettle applications, and this system can be used to find out who has the required device.

## Features

- Register - Form validation so @mettle.co.uk email address must be used, and password must be at least 6 characters long. All fields are required. Will also recognise if user is already registered, and will prompt for the log in page.
- Log In - If the user doesn't exist or password is wrong, page is rerendered with the previously entered email stored in the form, and user is prompted to check their log in details. A session token will be assigned as a cookie once logged in so users can access the secure pages.
- View Assets - Users can only see their own assets, Admins can view all user assets.
- Create Assets - When asset is created, a random 10 digit uuid is created. Form validation so all fields must be complete. Max field values in place.
- Edit Assets - Form validation so all fields must be complete. Max field values in place.
- Delete Assets - Admin users are able to delete any users assets, a modal will present to confirm the deletion.
- Log Out - Modal will be presented to confirm log out. Session cookie token will be deleted upon log out so secure pages cannot be accessed.

## Working Example

https://calson.pythonanywhere.com/

Admin email: admin@mettle.co.uk
Admin password: adminadmin

### Installation

Step-by-step instructions on how to install the application

Clone the repository:

```bash
git clone https://github.com/callumsontag/assetManagement.git
```

Navigate to where you have saved the project directory:

```
cd user/example/assetManagement
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python -m flask run
```
