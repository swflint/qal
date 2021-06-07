# Scrape Academic Library

This application is built to support automatically searching a number of academic digital libraries.  In particular, it currently supports the following:

 - [IEEE Xplore](https://ieeexplore.ieee.org)
 - [SpringerLink](https://link.springer.com)
 - [ScienceDirect](https://sciencedirect.com)

Other digital libraries and document repositories are in the works (including Wiley Online).

## Tools

### `query-acad-library`

## Obtaining API Keys

Confer with your institution & institutional library before doing so, however, it's fairly easy to obtain keys.

 - For IEEE Xplore: [register here](https://developer.ieee.org/member/register).  Place the API Key in `IEEE_XPLORE_API_KEY`.
 - For SpringerLink: [register here](https://dev.springernature.com/signup?cannot_be_converted_to_param).  Place the API Key in `SPRINGER_LINK_API_KEY`.
 - For ScienceDirect: [register here](https://dev.elsevier.com/apikey/manage).  Place the API Key in `SCIENCE_DIRECT_API_KEY`.

## Notes on Particular Backends

### SpringerLink

This must be accessed from your institutional IP address allocations.  Springer uses the requester IP as part of the authentication process.  Currently, their API does not give JSON-formatted responses on error: in this case, execution is stopped.

### ScienceDirect

This must also be accessed from your institutional IP address allocations.  Elsevier will limit results based on your institutions subscriptions (as far as I can tell, at least).  They handle quite well reporting of errors.  If you ever get an error message that is not handled, please make an issue.
