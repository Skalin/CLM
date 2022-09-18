# CLM

## Installation
1. Clone repository
2. Set up environment variables
3. Create a docker package using `docker build -t clm .`
5. Run package using `docker run clm`


### ENVIRONMENT variables
- ENV - if set to "DEVELOPMENT" then on update, the views and templates are reloaded automatically (just for active development needs), on production server set to "PRODUCTION"
- SECRET_KEY - Flask secret key for CSRF validation, this should be set on every single device randomly
- DEBUG - debug mode of flask application, in production this should be set to False or not set at all


### Development status
- v1.0 - migrating datasets to LKOD, ability to run as a singleton website
- v1.1 - added migrating files from CKAN to LKOD, code cleanup, json serializer and improved validation


### Future development updates
- v1.2 - improved configuration of migration
- v1.3 - rewriting ckan datasets and lkod users using interfaces to allow easier forking for other applications such as DKAN or others