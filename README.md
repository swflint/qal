# Query Academic Library

This application is built to support automatically searching a number of academic digital libraries.  In particular, it currently supports the following:

 - [IEEE Xplore](https://ieeexplore.ieee.org)
 - [SpringerLink](https://link.springer.com)
 - [ScienceDirect](https://sciencedirect.com)

## Tools

### `qal-query`

This tool can be used to try queries out on different digital libraries, as well as discover information about the capabilities and query options of each individual library.  Options of note include:

 - `-L` or `--list-libraries`: This option will list all libraries known to the system and their abbreviations.
 - `-d` or `--describe`: When coupled with `-l`, describe a library, showing the query option names available and their descriptions.
 - `-l` or `--library`: Select a library to query or describe.
 - `-r` or `--results`: Select where to store results.
 - `-q` or `--query`: Multiple allowed, should be of the form `query-option-name=value`.

### `qal-auto`

This tool is used to automatically run several queries against supported digital libraries.  There are several options, including:

 - `-p` or `--plan-file`: The location of the plan file.  Format described below.
 - `-s` or `--status-file`: Where to store query status (allows for picking back up if interrupted).
 - `-o` or `--output-file`: Where to store the results data.
 - `-b` or `--number-batches`: How many batches to run (how many times through one page of each query/provider pair).
 - `-v` or `--verbose`: Can show multiple times, more times is more verbose.

#### Plan Files

The plan file is a JSON-formatted dictionary, with at least the two following keys.

 - `sites`: an array of dictionaries.  Each dictionary contains minimum a `name`, and should contain a `key`, and can also contain `start` and `page_size` keys (integer values), and an optional `options` key with a dictionary of options.  See documentation for particular APIs.
 - `queries`: an array of dictionaries.  These dictionaries map query options (symbolic names, see `qal-query --describe -l library` for options) to string values.

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
