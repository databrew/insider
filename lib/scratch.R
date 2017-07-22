# Install the Rfacebook package from github
# devtools::install_github("pablobarbera/Rfacebook)

# Attach library for interfacing with facebook's graphi API
library(Rfacebook)

# Attach other assorted libraries
library(tidyverse)
library(yaml)

# Read in credentials from a gitignored file
creds <- yaml::yaml.load_file(input = '../credentials/credentials.yaml')

# Authorize
if('fb_oauth' %in% dir('../credentials')){
  load('../credentials/fb_oauth')
} else {
  # Upon first authentication, some manual steps
  # will have to be taken in the browswer. Follow
  # the directions here: http://thinktostart.com/analyzing-facebook-with-r/
  fb_oauth <- fbOAuth(app_id = creds$app_id, 
                      app_secret = creds$app_secret,
                      extended_permissions = TRUE)
  save(fb_oauth, file = '../credentials/fb_oauth')
  }

# Test by getting data on self
me <- getUsers("me",token=fb_oauth)

