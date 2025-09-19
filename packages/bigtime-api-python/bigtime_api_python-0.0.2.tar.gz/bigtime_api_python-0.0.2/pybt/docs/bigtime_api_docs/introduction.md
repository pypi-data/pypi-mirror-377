## Setup
- Visit the [BigTime API Documentation](https://iq.bigtime.net/BigtimeData/api/v2/help/Overview) page for information on how to get started
- Gather necessary [authentication information](docs/bigtime_api_docs/authentication.md)
- Save your Firm ID and api token in a .env file with the variables API for the API token and FIRM for the Firm ID

## API v2 Endpoints
Not all endpoints are supported or implemented yet. This is *not* an exhaustive list of the api endpoints, as I do not work at BigTime, and there is the possibility that these endpoints may change at any point without being reflected here. My firm also does not subscribe to all of BigTime's products, so there are endpoints I am unable to test. If you notice any endpoints are broken, please [submit an issue](https://github.com/N3RM/pybt/issues) or go ahead and fork the repo and submit a pull request with your updates!

To see what type of data is returned by each endpoint, please reference the [api documentation provided by BigTime](https://iq.bigtime.net/BigtimeData/api/v2/help/Overview).

See the [endpoint documentation](docs/bigtime_api_docs/endpoints/) for a list of API endpoints and which ones are implemented with the Python API wrapper as of 2025-09-02.